#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 13:38:56 2023

@author: felipe
"""

import pandas as pd 

import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime 
import os 
import hydroeval as he
import plotly.io as pio
#pio.renderers.default = 'svg'
pio.renderers.default = 'browser'

data_hoje = datetime.date.today()
start="2013-01-01 00:00:00"
end = "2015-12-31 00:00:00"
# end = "2023-04-07 00:00:00"

# start="2013-01-03 00:00:00"
# end = "2015-12-31 00:00:00"
def nse(predictions, targets):
    return (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))

obs = pd.read_csv("../calibracao_manual/tabelas/pm_vazao_obs.csv",index_col = 0,parse_dates=True)
obs = obs[start:end]
obs = obs.resample("D", closed='left', label='left').agg({'horleitura':(np.mean)})


# df_loc = "../exutorios_catch/out/"

# df_loc = "../exutorios_catch/out/"


def ler(df_loc):
    sim =  pd.read_csv(f'{df_loc}',skiprows=3)
    
    lista = []
    for i in sim["1"]:
        valor = i.split()[1]
        lista.append(float(valor))
    return lista


df_loc = "../catch/out/chanqWin.tss"
df_loc = "./resultados/9.tss"
lista = ler(df_loc)

df_loc = "./resultados/1.tss"
lista2 = ler(df_loc)

data = pd.date_range(start=start,end = end,freq = "D" )

df = pd.DataFrame(index = data)
df = df["2013":"2015"]
df["ls_dis"] = lista
df["0"] = lista2[:1095]
df.ls_dis = df.ls_dis.shift(2)
df["0"] = df["0"].shift(2)

df = pd.merge(df,obs,left_index= True,right_index= True)

log_nash = nse(np.log(df["ls_dis"]),np.log(df["horleitura"]))
nash = nse(df["ls_dis"],df["horleitura"])
df = df.fillna(df.mean())
kge, r, alpha, beta = he.evaluator(he.kge, df["ls_dis"], df["horleitura"])

integral_A = np.trapz(df["ls_dis"].fillna(df.ls_dis.mean()))

# Calcule a integral de B usando a Regra do Trapézio
integral_B = np.trapz(df["horleitura"].fillna(df["horleitura"].mean()))

# Calcule a diferença entre as integrais
diferenca = integral_B - integral_A



def cp(df,nome):
    df = df[nome]
    valores_ordenados = df.sort_values().to_frame()
    n = len(valores_ordenados)
    valores_ordenados["p"] = [(n-i+1)/(n+1) for i in range(n)   ]
    valores_ordenados["p-1"] = 1 - valores_ordenados["p"]
    return valores_ordenados

cp_sim = cp(df,"ls_dis")
cp_obs = cp(df,"horleitura")
cp_0 = cp(df,"0")
fig =  go.Figure()

fig.add_trace(go.Scatter(
    x = cp_sim.ls_dis,y = cp_sim.p,name = "simulado"
    ))
fig.add_trace(go.Scatter(
    x = cp_0["0"],y = cp_0.p,name = "original"
    ))
fig.add_trace(go.Scatter(
    x = cp_obs.horleitura,y = cp_obs.p,name = "obs"
    ))
fig.update_layout(title = f"periodo de {start.split('-')[0]}: {end.split('-')[0]}")
fig.show()
import xarray as xr
from plotly.subplots import make_subplots

chuva = xr.open_dataset("../catch/meteo/pr.nc").to_dataframe()
chuva =chuva.groupby("time").mean()
fig = make_subplots(specs = [[ { "secondary_y" : True}]])

fig.add_trace(go.Bar(x = chuva.index , y = chuva.pr,name = f"chuva",marker_color = "blue"),secondary_y=True)
fig.add_trace(go.Scatter(x = df.index , y = df.ls_dis,name = f"simulado nash: {round(nash,2)}",marker_color = "red"),secondary_y=False)
fig.add_trace(go.Scatter(x = df.index , y = df["0"],name = f"original: {round(nse(df['0'],df['horleitura']),2)}",marker_color = "green"),secondary_y=False)
fig.add_trace(go.Scatter(x= df.index,y=df.horleitura,name = "obs", marker_color = "black"),secondary_y=False)
fig.update_layout(title = f"periodo de {start.split('-')[0]}: {end.split('-')[0]}")
fig["layout"]["yaxis2"]["autorange"] = "reversed"
fig.show()
# Imprima os resultados
print("nash:",round(nash,2))
print("log_nash",round(log_nash,2))
print("kge,r,alpha,beta:",kge,r,alpha,beta)
print("Integral de A:", integral_A)
print("Integral de B:", integral_B)
print("Diferença entre as integrais:", round(diferenca,2), "em porcentagem:", abs(diferenca/integral_B))

print()
print("--------------#---------------")
print()
print(cp_sim.describe())
print()
print(cp_obs.describe())


#%% 
'''

analise sensibilidade


'''
# df_place = "../calibracao_manual/tabelas/resultados/_01.csv"
# df = pd.read_csv(df_place,index_col = 0)
# nome = df_place.split("/")[-1]
# fig = go.Figure()   
# fig.add_trace(go.Scatter(x = df.index , y =  obs["horleitura"],name = "obs"))
# fora = []
# for coluna in df.columns:

#     merged = obs.horleitura.to_frame()
#     merged["ls_dis"] = df[coluna].values
#     targets = merged["horleitura"]
#     predictions = merged["ls_dis"]
#     nash_value = (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))
#     print(nash_value)
#     dif = (abs(nash_value) - 0.299768776  )
#     if dif < 0.0003:
#         fora.append(coluna)
#     fig.add_trace(go.Scatter(x = df.index , y = df[coluna],name = f"{coluna} _>{nash_value}"))
# fig.show()
 
# fig =  go.Figure()
# fig.add_trace(go.Scatter(
#     x = cp_obs.horleitura,y = cp_obs.p,name = "obs"
#     ))
# fig.add_trace(go.Scatter(
#     x = cp_sim.ls_dis,y = cp_sim.p,name = "simulado"
#     ))
# for coluna in df.columns:
#     temp = cp(df,coluna)


#     fig.add_trace(go.Scatter(
#         x = temp[coluna],y = temp.p,name = coluna
#         ))
#     fig.update_layout(title = f"periodo de {start.split('-')[0]}: {end.split('-')[0]}")
# fig.show()