#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 15:00:21 2023

@author: felipe.bortolletto
"""

import os 
import pandas as pd 
import numpy as np 
from tqdm import tqdm
import xarray as xr
# dx = pd.read_csv("./tabelas/fator_param_ranges.csv",index_col = 0)

# thetas = "./params_calibration/soilhyd/thetas"
# thetar = "./params_calibration/soilhyd/thetar"
# saida = "../catch/maps/soilhyd/"

# lista = ["thetar1","thetar2"]
# files = [x for x in os.listdir(thetas)]
# [files.append(x) for x in [y for y in os.listdir(thetar)]]

# df = pd.DataFrame(columns = [dx.columns])
# df["ParameterName"] = [x.split(".")[0] for x in files]
# df["MinValue"] = [0 for x in range(len(files))]
# df["MaxValue"] = [1 for x in range(len(files))]
# df["DefaultValue"] = [0.48 for x in range(len(files))]
# df["tipo"] = ["thetas" if x<9 else "thetar" for x in range(len(files))]

# df["ON_OFF"] = ["ON" if x[0] in lista else "OFF" for x in df["ParameterName"].values ]

# df.to_csv("./tabelas/fator_thetas.csv",index =True)

df = pd.read_csv("./tabelas/fator_thetas.csv",index_col = 0)

def dds(Xmin, Xmax,X0, fobj, r=0.2, m=1000):
      # Passo 1

      Xmin = np.asarray(Xmin)
      Xmax = np.asarray(Xmax)
      # X0 = (Xmin + Xmax)/2
      D = len(Xmin)
      ds = [i for i in range(D)]
      dX = Xmax - Xmin
      # Passo 2
      I = np.arange(1, m+1, 1)
      Xbest = X0
      Fbest = fobj(Xbest)
      # Fbest =  abs(1 - fobj(X0))
      # Passo 3
      for i in tqdm(I):
          # print(i)
          Pi = 1 - np.log(i)/np.log(m)
          P = np.random.rand(len(Xmin))
          N = np.where(P < Pi)[0]
         
          if N.size == 0:
              N = [np.random.choice(ds)]
          # Passo 4
          Xnew = np.copy(Xbest)
          Xnew = np.array(Xbest, dtype=object)
          for j in N:
              # if j <= 18:
                  
                  Xnew[j] = Xbest[j] + r*dX[j]*np.random.normal(0, 1)
                  if Xnew[j] < Xmin[j]:
                      Xnew[j] = Xmin[j] + (Xmin[j] - Xnew[j])
                      if Xnew[j] > Xmax[j]:
                          Xnew[j] = Xmin[j]
                  elif Xnew[j] > Xmax[j]:
                      Xnew[j] = Xmax[j] - (Xnew[j] - Xmax[j])
                      if Xnew[j] < Xmin[j]:
                          Xnew[j] = Xmax[j]
              # else:
              #     matriz = np.random.uniform(Xmin[j], Xmax[j], size=(12, 20))

              #     Xnew[j] = matriz
          # Passo 5
          Fnew = fobj(Xnew)
          print(Fbest)
          if Fnew <= Fbest:
              Fbest = Fnew
              Xbest = np.copy(Xnew)
      # Fim
      return Xbest, Fbest 
  
def nse(predictions, targets):
    return (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))

  
def erro(X):
    
    df["DefaultValue"]= X
    settings_file = "../settings.xml"
    df.ON_OFF = [str(x) for x in df.ON_OFF]
    temp = df.loc[df.ON_OFF == "ON"]
    path_coleta = "./params_calibration/thetars_/"
    path_entrega = "../catch/maps/soilhyd/"
    for variavel,nome  in zip( temp.DefaultValue,temp.ParameterName) : 
             print(variavel,nome)
             dataset = xr.open_dataset(f"{path_coleta}{nome}.nc")
             name_var = list(dataset.variables)[-1] 
             dataset[name_var].values = [[variavel for _ in range(len(dataset.x))] for _ in range(len(dataset.y))]
             os.remove(f"{path_entrega}{nome}.nc")
             dataset.to_netcdf(f"{path_entrega}{nome}.nc")
    os.system(f"lisflood {settings_file}")
    
    df_loc = "../catch/out/"
    sim = pd.read_csv(f"{df_loc}/chanqWin.tss",skiprows=3)
    lista = []
    for i in sim["1"]:
        valor = i.split()[1]
        lista.append(float(valor))
    # ano_forcado = 2021
        
   
    obs = pd.read_csv("../calibracao_manual/tabelas/pm_vazao_obs.csv",index_col = 0,parse_dates=True)
    obs = obs["2013-01-01 00:00:00":"2015-12-31 00:00:00"]
    

    nash_value = nse(lista,obs["horleitura"])
    # return self.nash_value
    if nash_value > 1 :
        return (1 - (-nash_value))
    else:
        return (1 - nash_value)
    
X,F = dds(df.MinValue,df.MaxValue,df.DefaultValue,erro,r = 0.1,m = 200)
df.DefaultValue = X
df.to_csv("../validacao/resultados/thetas/calibra_thetas_1_2.csv",index = True)




#%%

def ler(df_loc):
    sim =  pd.read_csv(f'{df_loc}',skiprows=3)
    
    lista = []
    for i in sim["1"]:
        valor = i.split()[1]
        lista.append(float(valor))
    return lista

def reseta(X):
    df["DefaultValue"]= X
    df.ON_OFF = [str(x) for x in df.ON_OFF]
    temp = df.loc[df.ON_OFF == "ON"]
    path_coleta = "./params_calibration/thetars_/"
    path_entrega = "../catch/maps/soilhyd/"
    for variavel,nome  in zip( temp.DefaultValue,temp.ParameterName) : 
             print(variavel,nome)
             dataset = xr.open_dataset(f"{path_coleta}{nome}.nc")
             name_var = list(dataset.variables)[-1] 
             dataset[name_var].values = [[variavel for _ in range(len(dataset.x))] for _ in range(len(dataset.y))]
             os.remove(f"{path_entrega}{nome}.nc")
             dataset.to_netcdf(f"{path_entrega}{nome}.nc")




def modifica_uno(nome, fator):
    path_coleta = "./params_calibration/thetars_/"
    path_entrega = "../catch/maps/soilhyd/"
    temp = df.loc[df.ParameterName == nome]
    
    variavel =  fator
    dataset = xr.open_dataset(f"{path_coleta}{nome}.nc")
    name_var = list(dataset.variables)[-1] 
    print(temp )
    print(variavel)
    dataset[name_var].values = [[variavel for _ in range(len(dataset.x))] for _ in range(len(dataset.y))]
    print(dataset)
    os.remove(f"{path_entrega}{nome}.nc")
    dataset.to_netcdf(f"{path_entrega}{nome}.nc")
    
def plota():
    saidas = pd.DataFrame(index = data)
    files = [x for x in os.listdir("../validacao/resultados/thetas/") if x.endswith(".tss")]    
    # print(files)
    for arquivo in files:
        lista = ler(f"../validacao/resultados/thetas/{arquivo}")
        saidas[arquivo] = lista

    fig = go.Figure()
    fig.add_trace(go.Scatter(x = obs.index,y = obs.horleitura,name = "obs"))
    for columns in saidas:
        temp2 = saidas[columns]
        fig.add_trace(go.Scatter(x = temp2.index,y = temp2.values,name = columns))
    fig.show()
def move(nome):
    caminho_arquivo_destino = f"../validacao/resultados/thetas/{nome}"
    caminho_arquivo_origem = "../catch/out/chanqWin.tss"
    
    shutil.copy(caminho_arquivo_origem, caminho_arquivo_destino)
def plota_pastas():
    def chave_personalizada(elemento):
        partes = elemento.split('.')
        return float(partes[0])

    # Ordenar a lista usando a função de chave personalizada
    

    pastas = [
        f"../validacao/resultados/thetas/{nome}" for nome in df.loc[df.ON_OFF == "ON","ParameterName"]
              ]
    for pasta in pastas:
        files = ['0.001.tss', '0.01.tss', '0.1.tss', '0.2.tss', '0.3.tss', '0.4.tss', '0.5.tss', '0.6.tss', '0.8.tss', '0.9.tss', '1.tss']
        # files = sorted(files, key=chave_personalizada)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = obs.index,y = obs.horleitura,name = "obs"))
        for arquivo in files:
            print(arquivo)
            lista = ler(f"{pasta}/{arquivo}")
            fig.add_trace(go.Scatter(x =obs.index,y = lista,name = arquivo))
        fig.update_layout(
            title = pasta
            )
        fig.show()

# plota_pastas()
#%%
import shutil
import plotly.graph_objs as go
import plotly.io as pio
pio.renderers.default = 'browser'
start="2013-01-01 00:00:00"
end = "2015-12-31 00:00:00"
data = pd.date_range(start=start,end = end,freq = "D" )
df = pd.read_csv("../validacao/resultados/thetas/calibra_thetas_1_2.csv",index_col = 0)
obs = pd.read_csv("../calibracao_manual/tabelas/pm_vazao_obs.csv",index_col = 0,parse_dates=True)
obs = obs["2013-01-01 00:00:00":"2015-12-31 00:00:00"]

print(df.loc[df.ON_OFF == "ON"])
# nome = "thetar2_f"
# fator = 0.1692
# 



reseta(df.DefaultValue.values)

# numeros = [0.001,0.01,0.1,0.2,0.3,0.4,0.5,0.6,0.8,0.9,1]
# nome_t= df.loc[df.ON_OFF == "ON","ParameterName"]
# for tipo in nome_t :
#     for num in numeros:
#         modifica_uno(tipo,num)
#         os.system("lisflood ../settings.xml")
#         move(f"{tipo}/{num}.tss")
#         reseta(df.DefaultValue.values)
# # modifica_uno(nome, fator)
# 

#%%
#     #%%

move(f"somente os dois")
plota()
