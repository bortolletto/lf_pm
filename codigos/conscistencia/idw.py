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
locais = pd.read_csv("./csvs/loc_pontos_georeferenciado.csv",index_col = 0)
#%% SUBSTITUIR POR ARQUIVO REFERENTE AS ESTACOES DO SIMEPAR
dados = pd.read_csv("./chuva_editada.csv",index_col = 0,parse_dates = True)

dados = dados.drop(columns = ["media"])
locais.drop(index = 4815,inplace = True)
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
for ano in dados.index.year.unique():
    temp_loc = locais.copy()
    temp = dados
    for x,y in zip(pontos["x"],pontos["y"]):
        
        temp_loc['distancia'] = locais.apply(lambda row: calcular_distancia(x, y, row['cordx'], row['cordy']), axis=1)
        # temp_loc["distancia"] = temp_loc['distancia']/1000
        somatorio_distancias = sum([ x**-p for x in temp_loc["distancia"]])
        temp_loc['h'] = [(x**-p/somatorio_distancias) for x in temp_loc["distancia"]]
        
        for estacao in temp.columns:
            
            temp[estacao] = temp[estacao]* temp_loc.loc[temp_loc.nome == estacao,"h"].values[0]
            
        chuva_ano = temp.mean(axis = 1).to_frame()
        chuva_ano.rename(columns = {0:"chuva"},inplace = True)
        chuva_ano = chuva_ano.resample("D").sum(min_count = 20)
        # indice_x = (base_temp['x'] == x).argmax()
        # indice_y = (base_temp['y'] == y).argmax()
        
        
        for tempo in chuva_ano.index:
            indice_t = (base_temp['time'] == tempo).argmax()
            novo_valor = chuva_ano.loc[chuva_ano.index == tempo,"chuva"].values[0]
            base_temp.loc[{'time': tempo, 'x': x, 'y':y}] = novo_valor
    print(f"Estamos no ano de :{ano}")
            
# base_temp.to_netcdf("../../lf_pm/catch/meteo/chuvas/nova_chuva_atualiziada2.nc")
