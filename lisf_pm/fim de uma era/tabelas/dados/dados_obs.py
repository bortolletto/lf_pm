#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 09:12:24 2023

@author: felipe.bortolletto
"""

import pandas as pd
import os 


obs = pd.read_csv("/discolocal/felipe/git_pm/lisf_pm/novo_calibrador/tabelas/vazao_25334953_Pm.csv",index_col = 0,parse_dates= True)
obs.drop(columns=["horqualidade"],inplace = True)

obs = obs.resample("D",label = "right",closed = "right").mean()

obs_operacional = pd.read_csv("/discolocal/felipe/git_pm/lisf_pm/novo_calibrador/tabelas/pm_vazao_obs_antigo.csv",index_col = 0,parse_dates= True)

obs_operacional.rename(columns={"horleitura":"antigo"},inplace = True)
compara = pd.merge(obs,obs_operacional,left_index = True,right_index=True)


compara = compara["2013":]

import plotly.io as pio
import plotly.graph_objs as go
pio.renderers.default = 'browser'

fig = go.Figure()
fig.add_trace(go.Scatter(x = compara.index,y = compara.horleitura,name = "novo"))
fig.add_trace(go.Scatter(x = compara.index,y = compara.antigo,name = "antigo"))
fig.show()
#%%
obs = pd.read_csv("/discolocal/felipe/git_pm/lisf_pm/fim de uma era/tabelas/dados/pm_vazao_obs.csv",index_col =0,parse_dates =True)
obs['horleitura'].interpolate(method='linear', inplace=True)
obs.to_csv("/discolocal/felipe/git_pm/lisf_pm/fim de uma era/tabelas/dados/pm_vazao_obs.csv",index =True)

#%%
obs = pd.read_csv("/discolocal/felipe/git_pm/lisf_pm/novo_calibrador/tabelas/pm_vazao_obs.csv",index_col =0,parse_dates =True)

def cp(df,nome):
    df = df[nome]
    valores_ordenados = df.sort_values().to_frame()
    n = len(valores_ordenados)
    valores_ordenados["p"] = [(n-i+1)/(n+1) for i in range(n)   ]
    valores_ordenados["p-1"] = 1 - valores_ordenados["p"]
    return valores_ordenados

fig2 =  go.Figure()
fig = go.Figure()

# Personalize o layout do gráfico, se necessário
fig.update_layout(
    title='Hidrograma de Vazão',
    xaxis_title='Data',
    yaxis_title='Vazão',
)

# Mostre o gráfico
fig.show()

for ano in obs.index.year.unique():
    temp = obs[f"{ano}-01-01":f"{ano}-12-31"]
    # cp1 = cp(temp,"horleitura")
    cp1=temp.copy()
    cp1.rename(columns ={"horleitura":ano},inplace = True)
    
    fig2.add_trace(go.Histogram(x=cp1[ano], name=ano))
    
    fig.add_trace(go.Scatter(x = temp.index,y = temp.horleitura,name = ano))
fig.show()
fig2.show()

#%%

#%%


#%% dados de chuva

# files = os.listdir("./chuvas")
# final = pd.DataFrame()
# fig = go.Figure()

# for arquivo in files:
#     codigo = arquivo.split("_")[2]
#     temp = pd.read_csv(f"./chuvas/{arquivo}",index_col = 0,parse_dates= True)
#     temp = temp.loc[temp.horqualidade == 0]
#     temp = temp.resample("D",label = "right",closed = "right").sum(min_count = 4)
#     temp.drop(columns=["horqualidade"],inplace = True)
#     temp.rename(columns ={"horleitura":codigo},inplace = True)
#     final = pd.merge(final,temp,left_index=True,right_index=True,how = "outer")
#     fig.add_trace(go.Scatter(x = final.index,y = final[codigo],name = codigo))
    
# fig.show()

