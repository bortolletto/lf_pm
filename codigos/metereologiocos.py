#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 24 16:47:42 2023

@author: felipe.bortolletto

programa para gerar os mapas metegeologicos para o lisvap



#primeiramente temos que tratar cada um dos tipos de dados:
    

#iniciaremos com o vento 

"""
import wget
import numpy as np
import os
from osgeo import gdal
import pandas as pd 
import xarray as xr
import time

data = pd.date_range(start="2012-01-01", end="2023-05-23", freq="D")#
serie_final = "../dados/meteo/serie_final"

diretorios = [f for f in os.listdir("../dados/meteo/bruto") if f.endswith("_")]
for files_dir in diretorios:
    
    
    files = [f for f in os.listdir(f"../dados/meteo/bruto/{files_dir}") if f.endswith(".csv")]
    first = True
    for i in files:

                
        nome = i.split("_")[1]
        df = pd.read_csv(f"../dados/meteo/bruto/{files_dir}/{i}",index_col = 0,parse_dates = True)
        df = df.loc[df.horqualidade ==0]
        tipo = i.split("_")[0]
        if tipo == "radiaco":
            if i.split("-")[1] == "inemet.csv":
                df.horleitura = df.horleitura/3.6
            
        df = df.resample("D", closed='right', label='right').agg({'horleitura':(np.mean)})
        
        df.rename(columns = {"horleitura":nome},inplace = True)
       
        if first == True:
            final = pd.DataFrame(index = data)
            first = False
        final = pd.merge(final,df,left_index = True,right_index= True, how = "outer")
        final = final.mean(axis = 1)
        final = final.to_frame()
        final.rename(columns = {0:files_dir.split("_")[0]})
    print(files_dir.split("_")[0]," completo!")
    final.to_csv(f"../dados/meteo/serie_final/csv/{files_dir.split('_')[0]}.csv")

# calculemos agora a pressao de vapor:
hu = pd.read_csv(f"{serie_final}/csv/hu.csv",parse_dates = True,index_col = 0)
temp = pd.read_csv(f"{serie_final}/csv/t.csv",parse_dates = True,index_col = 0)

def pressao_vapor(hu, temp):
    b = 17.2694
    ezero = 6.113 #mbar
    t1 = 273.15
    t2 = 35.86
    
    temp1 = temp +273.15
    
    es = ezero * np.exp((b*(temp1["0"] - t1))/(temp1["0"] - t2))
    
    e = (hu/100)*es.to_frame()
    
    return e
pv = pressao_vapor(hu,temp)    
pv.to_csv(f"{serie_final}/csv/pd.csv")
#%%
'''
temos os dados prontos, falta agora a chuva
momentaneamente as bacias seram igualmente distribuidas, cada uma tera sua chuva
pm ->11 pixels
sb -> 8pixels
rn  -> 14 pixels
os pixels são contados de cima para baixo, e corresponde ao eixo y das latitudes. 
Vamos la!

'''


# data = pd.date_range(start="2012-01-01", end="2023-05-23", freq="D")#

pm = pd.read_csv("../dados/meteo/bruto/chuva/hist_precip_02_Porto_Amazonas.csv",index_col = 0,parse_dates = True)
pm = pm.resample("D", closed='right', label='right').agg({'chuva_mm':(np.sum)})
pm.rename(columns = {"chuva_mm":"pm"},inplace =True)

sb = pd.read_csv("../dados/meteo/bruto/chuva/hist_precip_03_Sao_Bento.csv",index_col = 0,parse_dates = True)
sb = sb.resample("D", closed='right', label='right').agg({'chuva_mm':(np.sum)})
sb.rename(columns = {"chuva_mm":"sb"},inplace =True)

rn = pd.read_csv("../dados/meteo/bruto/chuva/hist_precip_01_Rio_Negro.csv",index_col = 0,parse_dates = True)
rn = rn.resample("D", closed='right', label='right').agg({'chuva_mm':(np.sum)})
rn.rename(columns = {"chuva_mm":"rn"},inplace =True)

chuvas = pd.merge(pm,sb,left_index = True,right_index = True,how = "outer")
chuvas = pd.merge(chuvas,rn ,left_index = True,right_index = True,how = "outer")
chuvas.set_index(chuvas.index.strftime('%Y-%m-%d'))
chuvas.index = [x.replace(tzinfo=None) for x in chuvas.index]

data = chuvas.index

#agora pegaremos um raster base e atribuiremos a ele os valores de chuva
base = xr.open_dataset("../dados/base.tif")
x = base.x.values
y = base.y.values
        
    

lista = []
df_base = xr.open_dataset("../dados/base.nc").to_dataframe()
if len(df_base.columns) == 2:
    df_base.drop(columns =[df_base.columns.values[0]],inplace = True)
    nome = df_base.columns.values[0]
    df_base[nome] = 0
else:
    nome = df_base.columns.values[0]
    df_base[nome] = 0

temp = df_base.reset_index().pivot(index = "y",columns ="x",values = nome)
temp = temp.to_xarray()
temp =temp.sortby(temp.y,ascending = False).to_dataframe()
# temp.reindex(columns= list(temp.columns.values)[::-1])
contador = 0
contador =0
for i in temp.index:
    for z in temp.columns:
        temp[z].loc[temp.index == i] = contador
        contador +=1
base = temp
dct = {}
contador = 0
for y in base.index:
    contador+=1
    
    for x in base.columns:

        valor = int(base[x].loc[base.index ==y].values[0])

        dct[valor] = [x,y]

lista = []
for ponto in dct:
    lat = dct[ponto][1]
    lon = dct[ponto][0]
    t1= time.time()
    for t in data:
            if ponto <=200:
                valor = chuvas.loc[chuvas.index == t,"pm"].values[0]
                
            elif ponto <=360:
                valor = chuvas.loc[chuvas.index == t,"sb"].values[0]
            else: 
                valor = chuvas.loc[chuvas.index == t,"rn"].values[0]
                
            lista.append([t,lat,lon,valor])

    t2 = time.time()
    print(f"{ponto}/660 -> tempo de : {t2-t1}")

temp3 = pd.DataFrame(lista,columns =["time","y","x","pr"])
temp3.set_index(["time","y","x"],inplace = True)
temp3.to_xarray().to_netcdf(f"{serie_final}/ncs/pr.nc") 

#%%
from datetime import datetime
diretorios = [f for f in os.listdir(f"{serie_final}/csv") if f.endswith(".csv")]
for files_dir in diretorios:
    
    nome = files_dir.split(".")[0]
    df = pd.read_csv(f"{serie_final}/csv/{files_dir}",index_col = 0,parse_dates = True)
    df = df["2013-01-01":"2023-04-07"]
    df.rename(columns = {"0":nome},inplace = True)
    lista = []
    for ponto in dct:
        lat = dct[ponto][0]
        lon = dct[ponto][1]
        t1= time.time()
        for t in data:
                valor = df.loc[chuvas.index == t,nome].values[0]
                lista.append([t,lon,lat,valor])

        t2 = time.time()
        print(f"{nome}:  {ponto}/660 -> tempo de : {t2-t1}")

    temp3 = pd.DataFrame(lista,columns =["time","y","x","pr"])
    temp3.set_index(["time","y","x"],inplace = True)
    temp3.to_xarray().to_netcdf(f"{serie_final}/ncs/{nome}.nc") 

#%%

arquivos = [f for f in os.listdir(f"{serie_final}/ncs")]

for nc_file in arquivos:
    
    # nc_file = "/discolocal/felipe/LF_pratico/lfmetros/lisvap/dados brutos/testenew.nc"
    
    nc_dataset = xr.open_dataset(f"../dados/meteo/serie_final/ncs/{nc_file}")
        
    nome_nc = list(nc_dataset.variables)[-1]
    base = xr.open_dataset("../dados/meteo/base.nc")
    nome_base =     list(base.variables)[-1]
    if dict(nc_dataset.dims)["x"] == 33:
        base["time"] = nc_dataset["time"]
        base["y"] = nc_dataset["x"]
        base["x"] = nc_dataset["y"]
    else:
        base["time"] = nc_dataset["time"]
        base["x"] = nc_dataset["x"]
        base["y"] = nc_dataset["y"]
    base[nome_base] = nc_dataset[nome_nc]
    nome = nc_file.split(".")[0]
    base = base.rename({nome_nc:nome})
    base.to_netcdf(f"../dados/meteo/serie_final/finais/{nc_file}.nc")


