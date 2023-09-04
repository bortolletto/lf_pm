#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 16:46:20 2023

@author: felipe.bortolletto
Compara todos os resultados. :
    
"""

import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime 
import os 
data_hoje = datetime.date.today()

def nse(predictions, targets):
    print(predictions,targets)
    return (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))
            

obs = "/discolocal/felipe/lisflood_pm/vazoes_observadas"


df_loc = "../exutorios_catch/out/"
sim =  pd.read_csv(f'{df_loc}/chanqWin.tss',skiprows=9)

lista = []
for i in sim["7"]:
    valor = i.split()
    valor = valor[1:]
    lista.append(valor)

estacoes= [
        "vazao_25334953_Porto Amazonas",
        "vazao_25584963_Balsa Nova",
        "vazao_25604951_Guajuvira",
        "vazao_25604939_Araucária",
        "vazao_25594926_Ponte Do Umbarazinho",
        "vazao_25514921_ETE- Sanepar",
        "vazao_25484919_Ponte BR 277"
        ]
data = pd.date_range(start="2013-01-03 00:00:00",end = "2023-04-09 00:00:00",freq = "D" )
df = pd.DataFrame(index = data,columns = estacoes)

for estacoe,z in zip(estacoes,range(7)):
    df[estacoe] = [x[z] for x in lista]

pasta = f"/discolocal/felipe/lisflood_pm/vazoes_observadas/results/{data_hoje.day}_{data_hoje.month}"
# pasta = f"../exutorios_catch/out/novos_mapas/{data_hoje.day}_{data_hoje.month}"
if not os.path.exists(pasta):
    os.makedirs(pasta)
    print(f"Pasta '{pasta}' criada com sucesso.")
else:
    print(f"A pasta '{pasta}' já existe.")
with open(f'{pasta}/varios_exutorios.html', 'a') as f:
    
    fig = go.Figure()
    # obs = pd.read_csv(f"/discolocal/felipe/lisflood_pm/vazoes_observadas/{i}.csv",index_col = 0,parse_dates=True)
    # obs = obs["2013-01-01":"2023-04-07"]
    # fig.add_trace(go.Scatter(x= obs.index,y=obs.horleitura,name = "obs", marker_color = "black"))
    for i in df.columns:
        if i =="vazao_25594926_Ponte Do Umbarazinho":
            continue
        if i =="vazao_25484919_Ponte BR 277":
            continue
        if i =="vazao_25514921_ETE- Sanepar":
            continue
        temp = df[i].to_frame()
        
        if i == "vazao_25334953_Porto Amazonas":
            break
        temp[i] = [float(x) for x in temp[i]]
        # nash = nse(temp[i],temp["horleitura"])
    
    
        fig.add_trace(go.Scatter(x = temp.index , y = temp[i],name = i))
        fig.update_layout (
            title_text = "vazoes_exutorios")
    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))