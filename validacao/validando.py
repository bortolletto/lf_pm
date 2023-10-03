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
start="2021-01-01 00:00:00"
end = "2023-04-07 00:00:00"

# start="2013-01-03 00:00:00"
# end = "2015-12-31 00:00:00"
def nse(predictions, targets):
    return (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))

obs = pd.read_csv("../calibracao_manual/tabelas/pm_vazao_obs.csv",index_col = 0,parse_dates=True)
obs = obs[start:end]
obs = obs.resample("D", closed='left', label='left').agg({'horleitura':(np.mean)})


# df_loc = "../exutorios_catch/out/"
df_loc = "../catch/out/"
# df_loc = "../exutorios_catch/out/"
sim =  pd.read_csv(f'{df_loc}chanqWin.tss',skiprows=3)

lista = []
for i in sim["1"]:
    valor = i.split()[1]
    lista.append(float(valor))

data = pd.date_range(start=start,end = end,freq = "D" )
df = pd.DataFrame(index = data)
df["ls_dis"] = lista
df.ls_dis = df.ls_dis.shift(2)
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
    valores_ordenados["p"] = [(n-i+1)/(n+1) for i in range(n)]
    valores_ordenados["p-1"] = 1 - valores_ordenados["p"]
    return valores_ordenados

cp_sim = cp(df,"ls_dis")
cp_obs = cp(df,"horleitura")

fig =  go.Figure()

fig.add_trace(go.Scatter(
    x = cp_sim.ls_dis,y = cp_sim.p,name = "simulado"
    ))
fig.add_trace(go.Scatter(
    x = cp_obs.horleitura,y = cp_obs.p,name = "simulado"
    ))
fig.show()

fig = go.Figure()

fig.add_trace(go.Scatter(x = df.index , y = df.ls_dis,name = f"simulado nash: {nash}",marker_color = "red"))
fig.add_trace(go.Scatter(x= df.index,y=df.horleitura,name = "obs", marker_color = "black"))

fig.show()
# Imprima os resultados
print("nash:",nash)
print("log_nash",log_nash)
print("kge,r,alpha,beta:",kge,r,alpha,beta)
print("Integral de A:", integral_A)
print("Integral de B:", integral_B)
print("Diferença entre as integrais:", diferenca)

print()
print("--------------#---------------")
print()
print(cp_sim.describe())
print()
print(cp_obs.describe())
