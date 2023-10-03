#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 08:39:57 2023

@author: felipe.bortolletto
"""

import pandas as pd 
import os 
import plotly.graph_objects as go
import plotly.io as pio
import geopandas as gpd
import xarray as xr 
import math
pio.renderers.default='browser'

df = pd.read_csv("/discolocal/felipe/Progamas/coleta_dados/coleta/mapas_tcc/chuva_simepar/pm_verifica/dados.csv",index_col =0,parse_dates = True)
df = df.loc[df.horqualidade == 0]
df.drop(columns = ["horqualidade"],inplace = True)


hora = df.resample("H", closed='left', label='left').sum(min_count = 4)
df_dia = hora.resample("D", closed='left', label='left').sum(min_count = 20)
fig = go.Figure()
fig.add_trace(go.Scatter(x = df_dia.index,y = df_dia.horleitura))


files = [x for x in os.listdir("/discolocal/felipe/Progamas/coleta_dados/coleta/mapas_tcc/chuva_simepar/") if x.endswith(".csv")]
chuva = pd.DataFrame()
for arquivo in files:
  
    df = pd.read_csv(f"/discolocal/felipe/Progamas/coleta_dados/coleta/mapas_tcc/chuva_simepar/{arquivo}",index_col=0,parse_dates=True)
    df = df.loc[df.horqualidade == 0]
    df.drop(columns=["horqualidade"],inplace = True)
    df = df.resample("D", closed='left', label='left').sum(min_count = 70)
    df.rename(columns = {"horleitura":arquivo.split("_")[2]},inplace = True)
    chuva = pd.merge(chuva,df,left_index = True,right_index = True,how = "outer")
    # fig.add_trace(go.Scatter(x = df.index,y = df.horleitura))
# fig.show()


meus = xr.open_dataset("/discolocal/felipe/git_pm/catch/meteo/pr.nc").to_dataframe()
meus = meus.groupby("time").mean()


compara = chuva.mean(axis = 1).to_frame()
compara = pd.merge(compara,meus,left_index=True,right_index=True,how = "outer")
compara["pr"] = compara["pr"].shift(-1)
compara["dif"] = abs(compara["pr"] - compara[0])
compara = compara["2013":]
compara.drop(columns = ["spatial_ref"],inplace = True)

base=   xr.open_dataset("/discolocal/felipe/git_pm/catch/meteo/pr.nc")
compara = compara["2013":"2023-04-07"]
for ano in compara.index:
    dado = compara.loc[compara.index == ano,0].values[0]
    valores = [[dado for _ in range(len(base.x))] for _ in range(len(base.y))]
    base.loc[{"time":ano}].pr.values = valores

base.to_netcdf("/discolocal/felipe/git_pm/catch/meteo/chuvas/chuva_simepar_media_das_estacoes_simepar.nc")

#%%

import xarray as xr
import os
files = [x for x in os.listdir("./meteoln/")]

tn = xr.open_dataset("./meteoln/tn.nc")
pd = xr.open_dataset("./meteoln/pd.nc")
tx = xr.open_dataset("./meteoln/tx.nc")
ws = xr.open_dataset("./meteoln/ws.nc").to_dataframe()
rg = xr.open_dataset("./meteoln/rg.nc").to_dataframe()


def pressao_vapor_tetens(temperatura_celsius):
    """
    Calcula a pressão de vapor de água com base na equação de Tetens.

    Args:
    temperatura_celsius (float): A temperatura em graus Celsius.

    Returns:
    float: A pressão de vapor de água em milibares (mbar).
    """
    if temperatura_celsius < -100.0:
        raise ValueError("A temperatura está abaixo do limite de -100 °C, o que é irrealista.")
    
    # Constantes da equação de Tetens
    a = 17.62
    b = 243.12
    
    e = 6.112 * math.exp((a * temperatura_celsius) / (temperatura_celsius + b))
    
    return e

# Exemplo de uso da função
temperatura = 25.0  # Temperatura em graus Celsius
pressao_vapor = pressao_vapor_tetens(temperatura)

files = [x for x in os.listdir("/discolocal/felipe/Progamas/coleta_dados/coleta/lf/RG/")]

import pandas as pd
radiacao = pd.DataFrame()
for arquivo in files:
    df = pd.read_csv(f"/discolocal/felipe/Progamas/coleta_dados/coleta/lf/RG/{arquivo}",index_col = 0 ,parse_dates= True)
    df.rename(columns= {"horleitura":arquivo.split("_")[1]},inplace = True)
    radiacao = pd.merge(radiacao,df,left_index=True,right_index=True,how = "outer")
radiacao_soma = radiacao.sum(axis = 1).to_frame()
rg = xr.open_dataset("./meteoln/rg.nc")

for ano in radiacao_soma.index:
    dado = radiacao_soma.loc[radiacao_soma.index == ano,0].values[0]
    valores = [[dado for _ in range(len(rg.x))] for _ in range(len(rg.y))]
    rg.loc[{"time":ano}].radiacao.values = valores

rg.to_netcdf("/discolocal/felipe/git_pm/catch_lisvap/meteoln/rg.nc")
    
    #%%
    
tn = xr.open_dataset("/discolocal/felipe/git_pm/catch/meteo/tn.nc")
pd = xr.open_dataset("/discolocal/felipe/git_pm/catch/meteo/pd.nc")
tx = xr.open_dataset("/discolocal/felipe/git_pm/catch/meteo/tx.nc")
rg = xr.open_dataset("/discolocal/felipe/git_pm/catch/meteo/rg.nc").to_dataframe()
        
temp = tx.copy()
temp.temp_max.values =  (tx.temp_max + tn.temp_min)/2
temp = temp.to_dataframe()
base = xr.open_dataset("./meteoln/pd.nc").to_dataframe()
base["e0"] = [pressao_vapor_tetens(x) for x in temp.temp_max]
ds = xr.Dataset.from_dataframe(base)
ds.to_netcdf("/discolocal/felipe/git_pm/catch_lisvap/meteoln/pd.nc")


que = xr.open_dataset("/discolocal/felipe/git_pm/catch_lisvap/out/et.nc").to_dataframe()

vixe = pd.read_csv("/discolocal/felipe/git_pm/catch_lisvap/nova_resoc/dadosTN.csv")

#%%
files = [x for x in os.listdir("./nova_resoc")]
for pasta in files:
    # nome = arquivo.split("_")[0]
    files2 =  [x for x in os.listdir(f"./nova_resoc/{pasta}")]
    final= pd.DataFrame()
    for arquivo in files2:
        df = pd.read_csv(f"./nova_resoc/{pasta}/{arquivo}",index_col = 0 ,parse_dates= True)
        df = df[df.horqualidade ==0]
        df.drop(columns = ["horqualidade"],inplace = True)
        df.rename(columns = {"horleitura":arquivo.split("_")[1]},inplace =  True)
        final = pd.merge(final,df,left_index = True,right_index = True,how = "outer")
        final.to_csv(f"./nova_resoc/{pasta}.csv")
        
#%%import pandas as pd 
import os 
import plotly.graph_objects as go
import plotly.io as pio
import xarray as xr 
import math
import pandas as pd
def pressao_vapor_tetens(temperatura_celsius):
    """
    Calcula a pressão de vapor de água com base na equação de Tetens.

    Args:
    temperatura_celsius (float): A temperatura em graus Celsius.

    Returns:
    float: A pressão de vapor de água em milibares (mbar).
    """
    if temperatura_celsius < -100.0:
        raise ValueError("A temperatura está abaixo do limite de -100 °C, o que é irrealista.")
    
    # Constantes da equação de Tetens
    a = 17.62
    b = 243.12
    
    e = 6.112 * math.exp((a * temperatura_celsius) / (temperatura_celsius + b))
    
    return e
  
temp_media = pd.read_csv("./nova_resoc/tempmedia.csv",index_col = 0,parse_dates = True)
temp_media = temp_media .mean(axis = 1).to_frame()

temp_media[0] = [pressao_vapor_tetens(x) for x in temp_media[0]]
# temp_media.rename(columns = {0:"pd"},inplace = True)
    


temp_min = pd.read_csv("./nova_resoc/tempmin.csv",index_col = 0,parse_dates = True)
temp_min = temp_min .mean(axis = 1).to_frame()

print(temp_min.describe())

tempmax = pd.read_csv("./nova_resoc/tempmax.csv",index_col = 0,parse_dates = True)
tempmax = tempmax .mean(axis = 1).to_frame()

print(tempmax.describe())


vento = pd.read_csv("./nova_resoc/vento.csv",index_col = 0,parse_dates = True)
vento = vento .mean(axis = 1).to_frame()
print(vento.describe())
rad = pd.read_csv("./nova_resoc/rad.csv",index_col = 0,parse_dates = True)
rad = rad.sum(axis = 1).to_frame()

print(rad.describe())




base=   xr.open_dataset("/discolocal/felipe/git_pm/catch/meteo/pr.nc")


for df,nome in zip ([temp_media,temp_min,tempmax,vento,rad],["pr","tn","tx","ws","rg"]):
    df = df["2013":"2023-04-07"]
    for ano in df.index:
        dado = df.loc[df.index == ano,0].values[0]
        valores = [[dado for _ in range(len(base.x))] for _ in range(len(base.y))]
        base.loc[{"time":ano}].pr.values = valores
    print(nome)
    base.to_netcdf(f"./meteoln/{nome}.nc")
#%%
df = xr.open_dataset("/discolocal/felipe/git_pm/catch_lisvap/mapsln/dem.nc").to_dataframe()
# df = df[["y","x","Band1"]]
# df.to_netcdf("/discolocal/felipe/git_pm/catch_lisvap/mapsln/dem_.nc")

base = xr.open_dataset("/discolocal/felipe/git_pm/catch/maps/area.nc").to_dataframe()

test = pd.merge(base,df,left_index =True,right_index = True)
test.drop(columns = ["transverse_mercator","area","spatial_ref"],inplace =True)
ds = xr.Dataset.from_dataframe(test)
ds.to_netcdf("/discolocal/felipe/git_pm/catch_lisvap/mapsln/dem.nc")
#%%

e0 = xr.open_dataset("./out/e0.nc").to_dataframe()
es = xr.open_dataset("./out/es.nc").to_dataframe()
et = xr.open_dataset("./out/et.nc").to_dataframe()
et.describe()

