'''
--------------------------------------------------------------------------------
Modelo GR5i
--------------------------------------------------------------------------------
Implementacao - Bruno Juliani, jan/2021
Modificação do modelo GR4J implementado por Arlan Scortegagna
--------------------------------------------------------------------------------
Forcantes:
    PME - numpy.array 1D contendo a precipitacao medial espacial (mm)
    ETP - numpy.array 1D contendo a evapotranspiracao potencial (mm)
--------------------------------------------------------------------------------
Parametros:
    dt - passo de tempo (hrs)
    x1 - capacidade do reservatorio de producao (mm)
    x2 - coeficiente de troca de água c/ aquifero (mm/dt)
    x3 - capacidade de referência do reservatorio de propagacao (mm)
    x4 - tempo de base dos HUs (proporcional a dt)
    x5 - parâmetro relacionado a troca c/ aquifero (valor limite em que função
            de troca muda de sinal - entre 0 e 1)
--------------------------------------------------------------------------------
Variaveis de Estado :
    I - armazenamento do reservatório de interceptação (mm)
    S - armazenamento do reservatorio de producao (mm)
    R - armazenamento do reservatorio de propagacao (mm)
    HU1 - numpy.array 1D contendo os estados iniciais do HU 1 (mm)
    HU2 - numpy.array 1D contendo os estados iniciais do HU 1 (mm)
--------------------------------------------------------------------------------
Outros:
    area - area da bacia em km2 para conversao mm->m3/s (parametro constante)
    dt - passo de tempo (horas)
--------------------------------------------------------------------------------
Observações e recomendações:
    O equacionamento está de forma a possibilitar a aplicação para passos de
    tempo sub-diarios, dt.
    Para dt = 1 dia é recomendado capacidade de interceptação igual a zero.

--------------------------------------------------------------------------------

'''

import hydroeval as he

import numpy as np
from sklearn.metrics import mean_squared_error
def ordenadas_HU1(x4, D):
    n = int(np.ceil(x4))
    SH1 = np.zeros(n+1)
    for t in range(0, n+1):
        if (t<=0):
            SH1[t] = 0
        elif (t>0) & (t<x4):
            SH1[t] = (t/x4)**D
        else:
            SH1[t] = 1
    OrdHU1 = np.diff(SH1)
    return OrdHU1, n


def ordenadas_HU2(x4, D):
    m = int(np.ceil(2*x4))
    SH2 = np.zeros(m+1)
    for t in range(0, m+1):
        if (t<=0):
            SH2[t] = 0
        elif (t>0) & (t<=x4):
            SH2[t] = (1/2)*(t/x4)**D
        elif (t>x4) & (t<2*x4):
            SH2[t] = 1 - (1/2)*(2-t/x4)**D
        else:
            SH2[t] = 1
    OrdHU2 = np.diff(SH2)
    return OrdHU2, m


def simulacao(dt,area, PME, ETP, Qmon, x1, x2, x3, x4, x5, Estados=None):
    '''
    Variaveis internas
        Imax = capacidade maxima de interceptacao
        P1 - altura de precipitacao do passo de tempo
        E  - altura de evapotranspiracao potencial do passo de tempo
        Pn - precipitacao liquida
        En - evapotranspiracao potencial liquida
        Ps - montante de precipitacao que entra no reservatorio de SMA
        Es - montante que sai por evapotranspiracao do reservatorio de SMA
        Perc - montante percolado
        Pr - 'precipitacao efetiva' (na verdade, considera tb o PERC)
    '''

    # Constantes (passiveis de analise e estudo de caso)
    power = 4
    split = 0.9
    D     = 2.50 # p/ modelos horarios, D = 1.25 (ver Ficchi, 2017, p. 51)
    beta  = 5.25*(1/dt)**0.25

    # Calcula as ordenadas do HUs
    OrdHU1, n = ordenadas_HU1(x4, D)
    OrdHU2, m = ordenadas_HU2(x4, D)

    #Cálculo Interceptacao Maxima
    I = 0
    I_list = []
    for P1, E in np.nditer([PME,ETP]):
        #Perda de interceptao
        Ei = min(E, P1 + I)
        #Capacidade de evapotranspiracao
        En = E - Ei
        #Precipitacao efetiva
        Pn = P1 - Ei
        #Atualiza Interceptacao
        I = I + (P1 - Ei - Pn)
        I_list.append(I)
    Imax = max(I_list)

    # Atribui os estados iniciais
    if Estados is None:
        Estados = {}
    S = Estados.get('S', 0.6*x1)
    R = Estados.get('R', 0.7*x3)
    I = 0
    HU1 = Estados.get('HU1', np.zeros(n))
    HU2 = Estados.get('HU2', np.zeros(m))


    # Executa o processo iterativo
    Q = np.array([], float)
    Ps = 0
    for P1, E, Qm in np.nditer([PME,ETP,Qmon]):

        #INTERCEPTACAO
        #Perda de interceptao
        Ei = min(E, P1 + I)
        #Capacidade de evapotranspiracao
        En = E - Ei
        #Precipitacao efetiva
        Pn = P1 - Ei
        Pth = max(0, P1 - (Imax - I) - Ei)
        #Atualiza Interceptacao
        I = I + (P1 - Ei - Pn)

        #VAZAO MONTANTE
        #Soma vazao de montante ao reservatorio inicial
        Qmt = Qm*((3.6*dt)/area)
        S = S + Qmt

        #PRODUCAO
        #Chuva e evapotranspiracao real
        if En > 0:
            #tangente hiperbolica tende a 1 (arredondamento p/ x > 13)
            TWS = 1 if En/x1 > 13 else np.tanh(En/x1)
            Es = S*(2 - S/x1)*TWS / (1 + (1 - S/x1)*TWS)
            S = S - Es
            Pr = 0 # (manter pq depois vai somar com o Perc)
        else:
            #tangente hiperbolica tende a 1 (arredondamento p/ x > 13)
            TWS = 1 if Pth/x1 > 13 else np.tanh(Pth/x1)
            Ps = x1*(1 - (S/x1)**2)*TWS / (1 + (S/x1)*TWS)
            S = S + Ps
            Pr = Pn - Ps

        #Percolacao
        Perc = S*(1 - (1 + (S/(beta*x1))**power)**(-1/4))
        S = S - Perc

        #Routed water amount
        Pr += Perc

        #HIDROGRAMAS UNITARIOS
        # Convolucao do HU1
        HU1 += OrdHU1*(Pr*split)
        Q9 = HU1[0]
        HU1 = np.roll(HU1, -1)
        HU1[-1] = 0

        # Convolucao do HU2
        HU2 += OrdHU2*(Pr*(1-split))
        Q1 = HU2[0]
        HU2 = np.roll(HU2, -1)
        HU2[-1] = 0

        #TROCA COM AQUIFERO
        # Troca potencial com o aquifero (ganho ou perda)
        F = x2*((R/x3) - x5)
        if F > 0:
            F = 2*F
        else:
            F = -(min(abs(F), R + Q9) + min(abs(F), Q1))

        #ROUTING STORE
        # Atualiza o reservatorio de propagacao com output do HU1 (Q9)
        # Atualiza reservatorio de propagacao com troca c aquifero
        R = max(0, R + Q9 + F)
        Qr = R*(1 - (1 + (R/x3)**power)**(-1/4))
        R = R - Qr

        #ESCOAMENTO PSEUDO-DIRETO
        # Componente de escoamento pseudo-direto provem do HU2 (Q1)
        # Atualiza escoamento com troca c aquifero
        Qd = max(0, Q1 + F)

        #VAZAO SIMULADA
        Q = np.append(Q, Qr + Qd)

    #TRANSFORMA MM EM M3/S
    Q = Q*(area/(3.6*dt))

    return Q

#%%

from tqdm import tqdm
import pandas as pd




def dds(Xmin, Xmax, fobj, r=0.2, m=1000):
    # Passo 1

    Xmin = np.asarray(Xmin)
    Xmax = np.asarray(Xmax)
    X0 = (Xmin + Xmax)/2
    D = len(Xmin)
    ds = [i for i in range(D)]
    dX = Xmax - Xmin
    # Passo 2
    I = np.arange(1, m+1, 1)
    Xbest = X0
    Fbest = fobj(Xbest)
    # Passo 3
    for i in tqdm(I):
       
        Pi = 1 - np.log(i)/np.log(m)
        P = np.random.rand(len(Xmin))
        N = np.where(P < Pi)[0]
        
        if N.size == 0:
            N = [np.random.choice(ds)]
        # Passo 4
        Xnew = np.copy(Xbest)
        
        for j in N:
            Xnew[j] = Xbest[j] + r*dX[j]*np.random.normal(0, 1)
            if Xnew[j] < Xmin[j]:
                Xnew[j] = Xmin[j] + (Xmin[j] - Xnew[j])
                if Xnew[j] > Xmax[j]:
                    Xnew[j] = Xmin[j]
            elif Xnew[j] > Xmax[j]:
                Xnew[j] = Xmax[j] - (Xnew[j] - Xmax[j])
                if Xnew[j] < Xmin[j]:
                    Xnew[j] = Xmax[j]

        Fnew = fobj(Xnew)
        if Fnew < 1 and abs(1 - Fnew) < abs(1 - Fbest):
            Fbest = Fnew
            Xbest = np.copy(Xnew)
            print(Fbest)
    # Fim
    return Xbest, Fbest


def erro(X):
       x1, x2, x3, x4, x5= X
       targets = df['vazao']
       predictions = simulacao(dt,A,df["horleitura"],df["etp"],0,x1,x2,x3,x4,x5)
       nash_value = (np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2))
       kge, r, alpha, beta = he.evaluator(he.kge, predictions, targets)
       # print(1 - nash_value)
        # MSE = mean_squared_error(targets,predictions)
        
        # RMSE = np.sqrt(MSE)
       return kge[0]
       # print(nash_value)
       # if nash_value > 1 :
       #     return (1 - (-nash_value))
       # else:
       #     return (1 - nash_value)


if __name__ =='__main__':
    # Xmin = [20,-5,20,1,0]
    # Xmax = [1200,3,500,1,1]
    df = pd.read_csv("./dados_gr4j_pm.csv",index_col = 0 ,parse_dates = True)
    Xmin = [1,-100,1,1,0]
    Xmax = [9999,100,1000,5,1]
    A = 3623.74
    dt = 24
    xbest_f,fbest_f = dds(Xmin,Xmax,erro,r= 0.2,m = 1000)
    
    Q_fore = simulacao(dt,A,df["horleitura"],df["etp"],0,xbest_f[0],xbest_f[1],xbest_f[2],xbest_f[3],xbest_f[4])
   
    targets = df['vazao']
    predictions = Q_fore
    nash_value = (np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2))

    
    # fig, ax = plt.subplots()
    # line1, = ax.plot(df.index, df.vazao     , label='Obs. Flows ')
    # line2, = ax.plot(df.index, Q_fore ,  label=f'sim: nash>{round(nash_value,2)}')
    # ax.legend(loc='upper right')
    # plt.show()

    import plotly.graph_objs as go
    import plotly.io as pio
    pio.renderers.default='browser'
    fig = go.Figure()

    fig.add_trace(go.Scatter(x = df.index, y = df.vazao  ,name = "obs",marker_color = "black"))
    fig.add_trace(go.Scatter(x = df.index,y =  Q_fore ,name = "sim", marker_color = "red"))
    # fig.write_html("/home/felipe.bortolletto/Downloads/test.html")
    fig.show()
    
    df["Q_fore"] = Q_fore
    df.to_csv("./saida_gr4j.csv")
