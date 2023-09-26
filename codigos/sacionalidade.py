#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 14:02:30 2023

@author: felipe.bortolletto

analise temporal sacionalidade de porto amazonas

"""

import pandas as pd 
import plotly.io as pio
pio.renderers.default='browser'

vazao = pd.read_csv("/discolocal/felipe/git_pm/codigos/tabelas/vazao_obs_PM_2012.csv",index_col = 0,parse_dates = True)

chuva = pd.read_csv("../calibracao_manual/tabelas/chuva_editada.csv",index_col = 0,parse_dates = True)
chuva = chuva.media.to_frame()

df=pd.merge(vazao,chuva,left_index=True,right_index=True,how = "outer")
df.rename(columns = {"media":"chuva",
                     "horleitura":"vazao"
                     },inplace = True)
ha = pd.read_csv("/discolocal/felipe/git_pm/codigos/tabelas/chuva_25334953_Pm_lf.csv",index_col = 0,parse_dates = True) 
he = pd.read_csv("/discolocal/felipe/hidrolgoia_estatistica/chuva/csvs/chuva_25334953_Porto Amazonas.csv",index_col = 0,parse_dates = True)
he = he.resample("D",label = "left",closed = "left").sum()
ho=pd.merge(ha,he,left_index=True,right_index=True,how = "outer")
#%%




#%%
import plotly.graph_objects as go 


def multiplot(df_axisy,df_axisx):
    from plotly.subplots import make_subplots
    

    fig = make_subplots(specs = [[ { "secondary_y" : True}]])
    fig.add_trace(
        go.Bar(x =df_axisy.index ,y = df_axisy[df_axisy.columns.values[0]],name = "chuva"),secondary_y = True)
    fig.add_trace(
        go.Scatter(x = df_axisx.index,y = df_axisx[df_axisx.columns.values[0]],name = "Simulado"),secondary_y = False)

    fig.update_layout (
        title_text = "chuva vazao",
        autosize = True,
        width = 1800
        
        )
    fig["layout"]["yaxis2"]["autorange"] = "reversed"
    fig.show()
    return fig

nova_coleta = pd.read_csv("/discolocal/felipe/git_pm/codigos/tabelas/vazao_25334953_Pm_lf.csv",index_col = 0,parse_dates = True)
juntos = pd.merge(vazao,nova_coleta,left_index=True,right_index=True)


multiplot(chuva,vazao)

#%%plo de série temporal aleatória
import numpy as np 
import matplotlib.pyplot as plt
df_mes = df.resample("M",label = "right",closed = "right").agg(
    {
     "chuva":np.sum,
     "vazao":np.mean
     }
    )

semestre = (df.index.month - 1) // 6 + 1
bimestre =  ((df.index.month - 1) // 2) + 1
# Crie uma nova coluna para representar o trimestre
df['trimestre'] =  df.index.year.astype(str) + '-Q' + df.index.quarter.astype(str)
df['semestre']  =  df.index.year.astype(str) + '-S' + semestre.astype(str)
df["bimestre"]  =  df.index.year.astype(str) + '-B' + bimestre.astype(str)


trimestre = df.groupby('trimestre')["chuva"].sum().to_frame()
trimestre["trim"] = [x.split("-")[1] for x in trimestre.index]
trimestre["ano"] = [x.split("-")[0] for x in trimestre.index]
trimestre = trimestre.reset_index()
separados = pd.DataFrame(index =trimestre["ano"].unique())
separados['Q1'] = trimestre.loc[trimestre.trim == "Q1","chuva"].values
separados['Q2'] = trimestre.loc[trimestre.trim == "Q2","chuva"].values
separados['Q3'] = trimestre.loc[trimestre.trim == "Q3","chuva"].values
separados['Q4'] = np.append(trimestre.loc[trimestre.trim == "Q4","chuva"].values,np.nan)

separados = separados.round(2)
separados.describe()

separados.plot(kind='line', title='Dados de Q1, Q2, Q3 e Q4 ao longo do Tempo', xlabel='Ano', ylabel='Valores')
plt.legend(loc='upper left')
plt.show()
fig = go.Figure()

# Adicione uma linha para cada coluna de dados
for coluna in separados.columns:
    fig.add_trace(go.Scatter(x=separados.index, y=separados[coluna], mode='lines', name=coluna))

# Personalize o layout do gráfico
fig.update_layout(
    title='Dados de Q1, Q2, Q3 e Q4 ao longo do Tempo',
    xaxis=dict(title='Ano'),
    yaxis=dict(title='Valores'),
    legend=dict(x=0, y=1)
)

# Exiba o gráfico interativo
fig.show()


#%%
trimestre = df.groupby('trimestre')["vazao"].mean().to_frame()
trimestre["trim"] = [x.split("-")[1] for x in trimestre.index]
trimestre["ano"] = [x.split("-")[0] for x in trimestre.index]
trimestre = trimestre.reset_index()
separados = pd.DataFrame(index =trimestre["ano"].unique())
separados['Q1'] = trimestre.loc[trimestre.trim == "Q1","vazao"].values
separados['Q2'] = trimestre.loc[trimestre.trim == "Q2","vazao"].values
separados['Q3'] = trimestre.loc[trimestre.trim == "Q3","vazao"].values
separados['Q4'] = np.append(trimestre.loc[trimestre.trim == "Q4","vazao"].values,np.nan)

separados.round(2)
separados.describe()

multiplot(df_mes.chuva.to_frame(),df_mes.vazao.to_frame())


fig = go.Figure()
for ano in df_mes.index.year.unique():
    temp = df_mes.loc[df_mes.index.year == ano]
    fig.add_trace(go.Scatter(x = temp.index.month,y = temp.chuva,name = ano))

fig.show()
