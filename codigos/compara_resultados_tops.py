#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 13:49:38 2023

@author: felipe.bortolletto
"""
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime 
import os 
data_hoje = datetime.date.today()

def nse(predictions, targets):
    return (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))
            
# df_loc = "../exutorios_catch/out/"
df_loc = "../catch/out/"
# df_loc = "../exutorios_catch/out/"
sim =  pd.read_csv(f'{df_loc}chanqWin.tss',skiprows=3)

lista = []
for i in sim["1"]:
    valor = i.split()[1]
    lista.append(float(valor))
data = pd.date_range(start="2013-01-03 00:00:00",end = "2023-04-09 00:00:00",freq = "D" )
df = pd.DataFrame(index = data)
df["ls_dis"] = lista
# temp = pd.read_csv("/discolocal/felipe/lisflood_pm/vazoes_observadas/results/1_9/ultimo_vazao.csv",index_col = 0)
# df["ls_dis"] = temp["vazao_25334953_Porto Amazonas"].values
# obs = pd.read_csv("/discolocal/felipe/Progamas/coleta_dados/coleta/mapas_tcc/vazao/vazao_25334953_Porto Amazonas.csv",index_col = 0,parse_dates=True)
# obs.drop(columns = ["horqualidade"],inplace = True)
obs = pd.read_csv("/discolocal/felipe/lisflood_pm/vazoes_observadas/vazao_25334953_Porto Amazonas.csv",index_col = 0,parse_dates=True)
obs = obs["2013-01-01":"2023-04-07"]
obs = obs.resample("D", closed='left', label='left').agg({'horleitura':(np.mean)})

df = pd.merge(df,obs,left_index= True,right_index= True)

df = df["2013-01-01":"2023-04-07"]
nash = nse(df["ls_dis"],df["horleitura"])
fig = go.Figure()

fig.add_trace(go.Scatter(x = df.index , y = df.ls_dis,name = f"simulado nash: {nash}",marker_color = "red"))
fig.add_trace(go.Scatter(x= df.index,y=df.horleitura,name = "obs", marker_color = "black"))

pasta = f"../catch/out/novos_mapas/{data_hoje.day}_{data_hoje.month}"
# pasta = f"../exutorios_catch/out/novos_mapas/{data_hoje.day}_{data_hoje.month}"

if not os.path.exists(pasta):
    os.makedirs(pasta)
    print(f"Pasta '{pasta}' criada com sucesso.")
else:
    print(f"A pasta '{pasta}' já existe.")
fig.write_html(f"{pasta}/nova_chuva_estac_atualizado.html")


#%%


# diretorio = "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas copia/catch/table2map/"
# files = [x for x in os.listdir(diretorio) if x.endswith(".nc")]
# for i in files:
    
#     dataset = xr.open_dataset(f"{diretorio}{i}")
#     dataset = dataset.sel(band=1)
#     dataset = dataset.drop("band")
#     os.remove(f"{diretorio}{i}")
#     dataset.to_netcdf(f"{diretorio}{i}")
    
# df = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas copia/catch/table2map/soildepth2_f.nc")
# df.band_data.values = df.band_data.values/10
# os.remove("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas copia/catch/table2map/soildepth2_f.nc")
# df.to_netcdf("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas copia/catch/table2map/soildepth2_f.nc")
