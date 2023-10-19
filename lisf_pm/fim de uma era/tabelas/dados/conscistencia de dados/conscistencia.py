import pandas as pd
import os
import plotly.io as io
import plotly.graph_objs as go
import numpy as np
io.renderers.default='browser'
#%%ss

files = os.listdir("./chuva_simepar") 
data = pd.date_range("2010-01-01","2023-08-26",freq="1H")
diario = pd.DataFrame(index = data)
codigos = []
for est in files:
    try:
        codigo= est.split("_")[2]
    except:
        print(f"arquivo {est} não representa uma estacao")
        continue
    nome = est.split("_")[3].split(".")[0]
    df = pd.read_csv(f"./chuva_simepar/{est}",index_col = 0 ,parse_dates = True)
    
    df.rename(columns={"horleitura": nome,
                       
                       },inplace = True)
    df = df.loc[df.horqualidade == 0]
    df.drop(columns = ["horqualidade"],inplace = True)
    
    diario = pd.merge(diario,df,how = "outer",left_index=True,right_index=True)
    codigos.append(int(codigo))
final = diario.resample("D",closed = "right",label = "right").sum(min_count = 20)
media_antiga = final.mean(axis = 1)
final = final[:-2]
anual = final.resample("Y",closed = "right",label = "right").sum(min_count = 150)

estac = pd.read_csv("./estacoes_dados.csv")
estac.loc[estac.orgao == "SIMEPAR"]
estac = estac[estac['codigo'].isin(codigos)]
estac.to_csv("./chuva_simepar/estacoes_chuva.csv")


#%%
meu_dicionario = {
    1: 'Porto Amazonas',
    2: 'São Bento',
    3: 'Fazenda Gralha Azul-PUC',
    4: 'Vossoroca',
    5: 'Guaricana',
    6: 'Lapa',
    7: 'Barragem UHE Marumbi',
    8: 'Pinhais',
    9: 'Curitiba',
    10: 'Salto do Meio',
    11: 'Capivari Montante',
    12: 'Recanto do Maneco',
    13: 'media'
}


    
quadrantes = {
    "leste"    : [1,6,2],
    "sul"      : [3,5,10,4],
    "nordeste" : [11,12],
    "centro"   : [8,9,7]
    }



#%%
def plota(df,titulo,x = None,y = None,barras = False):
    fig = go.Figure() 
    if barras == True:
        for columns in df:
            fig.add_trace(go.Bar(x = df.index , y = df[columns],name = columns))
    else:   
        if x == None:
            for columns in df:
                
                fig.add_trace(go.Scatter(x = df.index , y = df[columns],name = columns,connectgaps = False))
                
        else:
                fig.add_trace(go.Scatter(x = x , y = y,name = columns))
    fig.update_layout (
        title_text = titulo,
        autosize = True,
        # width = 1800
        )
    fig.show()
    
    
    
def alterar_valores_para_nan_no_intervalo(identificador, df, data_inicial, data_final):
    identificador_ = meu_dicionario[identificador]
    try:
        df[identificador_][data_inicial : data_final] = np.nan
    except Exception as e:
        print(f"Ocorreu um erro: {str(e)}")
        
def remove_atraves_de_dct(dct):
    for key in dct.keys():
        temp1 = dct[key]
        for estac in temp1.keys():
            temp2 = temp1[estac]
            data_inicial = temp2[0][0]
            data_final = temp2[0][1]
            alterar_valores_para_nan_no_intervalo(estac,final,data_inicial,data_final)
            
def plot_curva_permanencia(data, xlabel, ylabel,nome):
    """
    Plota uma curva de permanência usando Plotly.

    Args:
        data (list or numpy array): Uma lista ou array de valores que você deseja plotar na curva de permanência.
        xlabel (str): Rótulo do eixo x.
        ylabel (str): Rótulo do eixo y.
    """

    # Classifique os dados em ordem crescente
    fig = go.Figure()
    for columns in data:
        # sorted_data = np.sort(data[columns])
    
        # # Calcule a distribuição acumulada
        # cumulative_data = np.arange(1, len(sorted_data) + 1) / len(sorted_data) * 100
    
        # Crie o gráfico usando Plotly
        sorted_data = data[columns].sort_values().to_frame()
        n = len(sorted_data)
        sorted_data["p"] = [(n-i+1)/(n+1) for i in range(n)]
        sorted_data["p-1"] = 1 - sorted_data["p"]

        # vazao_desejada = sorted_data.loc[sorted_data["p-1"] <= Q+0.0001]
        # vazao_desejada = vazao_desejada.iloc[-1].vazao
        
        fig.add_trace(go.Scatter(y=sorted_data[columns], x=sorted_data["p"], mode='lines',connectgaps = False,name = columns))
        fig.update_layout(
            title=f'Curva de Permanência {nome}',
            # xaxis_title=xlabel,
            # yaxis_title=ylabel,
        )

    # Exiba o gráfico
    fig.show()

#%%
def substituir_nulos_pela_media_da_linha(row):
    row_mean = row.mean()
    return row.fillna(row_mean)

elementos_a_remover = ['Fazenda Gralha Azul-PUC','Barragem UHE Marumbi','Recanto do Maneco']
def prenche_falhas(final):
    for keys in quadrantes.keys():
        estac = [meu_dicionario[x] for x in quadrantes[keys]]    
        estac = [x for x in estac if x not in elementos_a_remover]
        temp = final[estac]
        temp = temp.apply(substituir_nulos_pela_media_da_linha, axis=1)
        for elemento in temp.columns:
            final[elemento] = temp[elemento]
    print("falhas preenchidas")
    return 

    
    
# plota(final,"chuva_diaria")
# plota(anual,"chuva_anual")
# plot_curva_permanencia(final,"dados_organizados","acumulada","chuva")
# plota(final,"dados de chuva")
#%%

for key in quadrantes.keys():
    
    quadrante= quadrantes[key]
    lista_temp = [meu_dicionario[x] for x in quadrante]
    temp = final[lista_temp]
    acumulado_mensal = temp.resample("M",closed = "left",label = "right").sum(min_count = 23)
    acumulado_anual = temp.resample("Y",closed = "left",label = "right").sum(min_count = 200)
  
    plota(acumulado_mensal,f"quadrante {key} mensal",barras = True)
    
    plota(acumulado_anual,f"quadrante {key} anual",barras = True)
    
    plota(temp,f"quadrante {key}")

alteracoes = {
    "leste"   : {
        6:[("2016-08-23","2016-10-01"),("2016-03-21","2016-03-21")],
        2:[("2019-01-16","2019-03-15")]        
        },
    "sul"     : {
        3:[("2010-01-02","2023-08-27"),("2017-06-01","2017-09-31"),("2022-12-24","2023-02-26")],
        10:[("2013-12-16","2014-03-19"),("2017-06-09","2017-09-29")],
        },
    
    "nordeste": {
        12:[("2010-01-02","2023-08-27")],
        11:[("2012-08-01","2012-08-31"),("2017-06-01","2017-09-31"),("2022-12-24","2023-02-31")]
        },
    "centro"  : {
        7:[("2010-06-01","2010-9-01"),("2015-03-01","2015-03-31")],
        },
    }
remove_atraves_de_dct(alteracoes)
prenche_falhas(final)

final.drop(columns = elementos_a_remover,inplace = True)
final = final.apply(substituir_nulos_pela_media_da_linha,axis = 1)
final["media"] = final.mean(axis = 1)

fig = go.Figure() 

fig.add_trace(go.Scatter(x = final.index , y = media_antiga,name = "antiga"))
fig.add_trace(go.Scatter(x = final.index , y = final["media"],name = "nova"))

fig.update_layout (
    title_text = "compara medias chuva",
    autosize = True,
    # width = 1800
    )
fig.show()

final.to_csv("../chuva_editada.csv")
#%%vazao

files = os.listdir("./vazao_simepar")
data = pd.date_range("2010-01-01","2023-08-26",freq="1H")
final = pd.DataFrame(index = data)
codigos = []
for est in files:
    try:
        codigo= est.split("_")[2]
    except:
        print("arquivo {est} não representa uma estacao")
        continue
    nome = est.split("_")[3].split(".")[0]
    df = pd.read_csv(f"./vazao_simepar/{est}",index_col = 0 ,parse_dates = True)

    df.rename(columns={"horleitura": nome,
                       
                        },inplace = True)
    # df = df.loc[df.horqualidade == 0]
    df.drop(columns = ["horqualidade"],inplace = True)
    
    final = pd.merge(final,df,how = "outer",left_index=True,right_index=True)
    codigos.append(int(codigo))
final = final.resample("D",closed = "left",label = "right").mean()
final["media"] = final.mean(axis = 1)
anual = final.resample("Y",closed = "left",label = "right").mean()

plot_curva_permanencia(final,"dados_organizados","acumulada","vazaO")

estac = pd.read_csv("/discolocal/felipe/Progamas/coleta_dados/coleta_metadados/estações_dados.csv")
estac.loc[estac.orgao == "SIMEPAR"]
estac = estac[estac['codigo'].isin(codigos)]
estac.to_csv("./vazao_simepar/estacoes_vazao.csv")

#%%.
chuva = pd.read_csv("./chuva_editada.csv",index_col = 0,parse_dates = True)

chuva_média = chuva["media"]

import plotly.graph_objs as go
from plotly.subplots import make_subplots


def plota_com_chuva(df,titulo):
    fig = make_subplots(specs = [[ { "secondary_y" : True}]])
    fig.add_trace(
        go.Bar(x =final.index ,y = final.media,name = "chuva"),secondary_y = True)
    for elemento in df.columns:
        if elemento == "media":
            continue
        fig.add_trace(
            go.Scatter(x = df.index,y = df[elemento],name = elemento),secondary_y = False)
    fig.update_layout (
        title_text = titulo,
        autosize = True,
        # width = 1800
        
        )

    fig["layout"]["yaxis2"]["autorange"] = "reversed"
    fig.show()
    return
    
meu_dicionario = {
    1: 'Porto Amazonas',
    2: 'São Bento',
    3: 'Capivari Montante',
}
    

    
quadrantes = {
    "unico"    : [1,2,3],
    }



for key in quadrantes.keys():
    # key = "nordeste"
    quadrante= quadrantes[key]
    lista_temp = [meu_dicionario[x] for x in quadrante]
    temp = final[lista_temp]
    acumulado_mensal = temp.resample("M",closed = "left",label = "right").sum(min_count = 23)
    acumulado_anual = temp.resample("Y",closed = "left",label = "right").sum(min_count = 200)

    plota_com_chuva(temp,f"vazao")

# alteracoes = {
#     "leste"   : {
#         6:[("2016-08-23","2016-10-01"),("2016-03-21","2016-03-21")],
#         2:[("2019-01-16","2019-03-15"),("2023-01-24","2023-03-03")]        
#         },
#     "sul"     : {
#         3:[("2010-01-02","2023-08-27")],
#         10:[("2013-12-15","2014-03-18"),("2017-07-29","2017-09-29")],
#         },
    
#     "nordeste": {
#         12:[("2010-01-02","2023-08-27")],
#         },
#     "centro"  : {
#         7:[("2010-01-02","2023-08-27")],
#         },
#     }




# alterar_valores_para_nan_no_intervalo(1, final, "2010-01-02","2010-0

