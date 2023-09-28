#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  4 13:48:20 2023

@author: felipe.bortolletto
"""

import pandas as pd
import xarray as xr 
import numpy as np 

#
locais = pd.read_csv("/discolocal/felipe/git_pm/codigos/conscistencia/chuva_simepar/estacoes_chuva_proj.csv",index_col = 0)
#%% SUBSTITUIR POR ARQUIVO REFERENTE AS ESTACOES DO SIMEPAR
dados = pd.read_csv("./chuva_editada.csv",index_col = 0,parse_dates = True)

dados = dados.drop(columns = ["media"])
# locais.drop(index = 4815,inplace = True)
locais = locais[locais["nome"].isin(dados.columns)]

# estac = pd.read_csv("./csvs/estac_atualizado.csv",index_col = 0)


base = xr.open_dataset("../../catch/maps/outlets.nc").to_dataframe()
base_temp   = xr.open_dataset("../../catch/meteo/chuvas/pr.nc")


base_temp = base_temp.drop("spatial_ref")
# base_temp = base_temp.to_frame()
base = base.reset_index()
pontos = base[["x","y"]]

def calcular_distancia(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


    
# Calcula a distância para cada ponto no segundo DataFrame


#%%
p = 0.5
dados = dados["2013":"2023-04-07"]



# ano = 2013
for x,y in zip(pontos["x"],pontos["y"]):
    print(x,y)
    temp_loc = locais.copy()
    temp = dados.copy()
    temp_loc['distancia'] = locais.apply(lambda row: calcular_distancia(x, y, row['cordx'], row['cordy']), axis=1)
    # temp_loc["distancia"] = temp_loc['distancia']/1000
    somatorio_distancias = sum([ x**-p for x in temp_loc["distancia"]])
    temp_loc['h'] = [(x**-p/somatorio_distancias) for x in temp_loc["distancia"]]
    
    for estacao in temp.columns:
        
        temp[estacao] = temp[estacao]* temp_loc.loc[temp_loc.nome == estacao,"h"].values[0]
        
    chuva_ano = temp.sum(axis = 1).to_frame()
    chuva_ano.rename(columns = {0:"chuva"},inplace = True)
    # chuva_ano = chuva_ano.resample("D").sum(min_count = 20)
    # indice_x = (base_temp['x'] == x).argmax()
    # indice_y = (base_temp['y'] == y).argmax()
    
    
    for tempo in chuva_ano.index:
        indice_t = (base_temp['time'] == tempo).argmax()
        novo_valor = chuva_ano.loc[chuva_ano.index == tempo,"chuva"].values[0]
        # print(novo_valor)
        base_temp.loc[{'time': tempo, 'x': x, 'y':y}] = novo_valor
    base_temp.to_netcdf("/discolocal/felipe/git_pm/codigos/conscistencia/idw_soma.nc")
# print(f"Estamos no ano de :{ano}")
            
# base_temp.to_netcdf("../../lf_pm/catch/meteo/chuvas/nova_chuva_atualiziada2.nc")

#%% voronoi
import os 
files = [x for x in os.listdir("/discolocal/felipe/git_pm/codigos/conscistencia/chuva_simepar/")]
import xarray as xr 
import pandas as pd 

dados = pd.read_csv("./chuva_editada.csv",index_col = 0,parse_dates = True)
dados = dados.drop(columns = ["media"])
base_temp   = xr.open_dataset("../../catch/meteo/chuvas/pr.nc")
base_temp = base_temp.drop("spatial_ref")
voronoi = xr.open_dataset("/discolocal/felipe/git_pm/codigos/conscistencia/chuva_simepar/voronoi_estac_dados.nc").to_dataframe()
voronoi = voronoi.drop(columns = ["transverse_mercator"])
voronoi = voronoi.reset_index()

codigo_dados = {
    'Porto Amazonas': '25334953',
    'São Bento': '25564947',
    'Fazenda Gralha Azul-PUC': '25654927',
    'Vossoroca': '25494905',
    'voronoi.tif': None,
    'Guaricana': '25424858',
    'Lapa': '25474946',
    'Barragem UHE Marumbi': '25254856',
    'Pinhais': '25254905',
    'Curitiba': '25264916',
    'Salto do Meio': '25484859',
    'voronoi.nc': None,
    'Capivari Montante': '25134856',
    'Recanto do Maneco': '25184889'
}

voronoi = voronoi.replace(25334952.0,25334953.0)
voronoi = voronoi.replace(25254904.0,25494905.0)

dados = dados["2013":"2023-04-07"].rename(columns = codigo_dados)
for x,y in zip(voronoi["x"],voronoi["y"]):
    print(x,y)
    estac = str(int(voronoi.loc[(voronoi.x ==x) & (voronoi.y == y),"Band1"].values[0]))
    for tempo in dados.index:
       base_temp.loc[{'time': tempo, 'x': x, 'y':y}] = dados[estac].loc[dados.index == tempo].values[0]
base_temp.to_netcdf("/discolocal/felipe/git_pm/codigos/conscistencia/voroni_pr.nc")
    
    #%%
estacoes = pd.read_csv("/discolocal/felipe/git_pm/codigos/conscistencia/estacoes_dados.csv")
estacoes.codigo = [str(int(x)) for x in estacoes.codigo]
estacoes =   estacoes.loc[estacoes.codigo.isin(dados.columns)]
estacoes.to_csv("/home/felipe.bortolletto/Documentos/temp/estacoes.csv")
#%%
import xarray as xr 

df = xr.open_dataset("/discolocal/felipe/git_pm/catch/maps/antes modificados/chanflpn.nc")
df["chanflpn"] = df.chanflpn*100
os.remove("/discolocal/felipe/git_pm/catch/maps/chanflpn.nc")
df.to_netcdf("/discolocal/felipe/git_pm/catch/maps/chanflpn.nc")
