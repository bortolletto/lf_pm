#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 09:22:26 2023

@author: felipe.bortolletto

ARQUIVO PARA TESTAS OS DADOS DE USO DO SOLO E FRAÇÃO DE USO DO SOLO. 

"""

import subprocess
import xarray as xr
from osgeo import gdal
import os 
import pandas as pd
import plotly.graph_objs as go

#%%

fracs = "../catch/maps/landuse/old_ones/"
AGR = xr.open_dataset(f"{fracs}fracirrigated.nc")
FLO = xr.open_dataset(f"{fracs}fracforest.nc")
RIC = xr.open_dataset(f"{fracs}fracrice.nc")
OTH = xr.open_dataset(f"{fracs}fracother.nc")
SEA = xr.open_dataset(f"{fracs}fracsealed.nc")
WAT = xr.open_dataset(f"{fracs}fracwater.nc")


soma = AGR.fracirrigated.values+FLO.fracforest.values+RIC.fracrice.values+OTH.fracother.values+SEA.fracsealed.values+WAT.fracwater.values
contagem  = len(soma) * len(soma[0])
somatorio = int(soma.sum())

LISTA_0 = [[0 for _ in range(len(AGR.x))] for _ in range(len(AGR.y))]
LISTA_1 = [[1 for _ in range(len(AGR.x))] for _ in range(len(AGR.y))] 


AGR.fracirrigated.values = LISTA_1
FLO.fracforest.values    = LISTA_1
RIC.fracrice.values      = LISTA_1
OTH.fracother.values     = LISTA_1
SEA.fracsealed.values    = LISTA_1
WAT.fracwater.values     = LISTA_1

os.remove(f"../catch/maps/landuse/fracirrigated.nc")
os.remove(f"../catch/maps/landuse/fracforest.nc")
os.remove(f"../catch/maps/landuse/fracrice.nc")
os.remove(f"../catch/maps/landuse/fracother.nc")
os.remove(f"../catch/maps/landuse/fracsealed.nc")
os.remove(f"../catch/maps/landuse/fracwater.nc")

AGR.to_netcdf(f"../catch/maps/landuse/fracirrigated.nc")
FLO.to_netcdf(f"../catch/maps/landuse/fracforest.nc")
RIC.to_netcdf(f"../catch/maps/landuse/fracrice.nc")
OTH.to_netcdf(f"../catch/maps/landuse/fracother.nc")
SEA.to_netcdf(f"../catch/maps/landuse/fracsealed.nc")
WAT.to_netcdf(f"../catch/maps/landuse/fracwater.nc")


soma = AGR.fracirrigated.values+FLO.fracforest.values+RIC.fracrice.values+OTH.fracother.values+SEA.fracsealed.values+WAT.fracwater.values
contagem  = len(soma) * len(soma[0])
somatorio = int(soma.sum())
print(somatorio,"/",contagem)


# visualiza = xr.open_dataset(f"../catch/maps/landuse/fracforest.nc")
def reset():
    #funcao reseta as condiçoes originais
    fracs = "../catch/maps/landuse/old_ones/"
    AGR = xr.open_dataset(f"{fracs}fracirrigated.nc")
    FLO = xr.open_dataset(f"{fracs}fracforest.nc")
    RIC = xr.open_dataset(f"{fracs}fracrice.nc")
    OTH = xr.open_dataset(f"{fracs}fracother.nc")
    SEA = xr.open_dataset(f"{fracs}fracsealed.nc")
    WAT = xr.open_dataset(f"{fracs}fracwater.nc")
    
    os.remove(f"../catch/maps/landuse/fracirrigated.nc")
    os.remove(f"../catch/maps/landuse/fracforest.nc")
    os.remove(f"../catch/maps/landuse/fracrice.nc")
    os.remove(f"../catch/maps/landuse/fracother.nc")
    os.remove(f"../catch/maps/landuse/fracsealed.nc")
    os.remove(f"../catch/maps/landuse/fracwater.nc")
    
    AGR.to_netcdf(f"../catch/maps/landuse/fracirrigated.nc")
    FLO.to_netcdf(f"../catch/maps/landuse/fracforest.nc")
    RIC.to_netcdf(f"../catch/maps/landuse/fracrice.nc")
    OTH.to_netcdf(f"../catch/maps/landuse/fracother.nc")
    SEA.to_netcdf(f"../catch/maps/landuse/fracsealed.nc")
    WAT.to_netcdf(f"../catch/maps/landuse/fracwater.nc")
    return "Tudo permanece"
reset()
#%% altera soildp

# diretorio = "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/table2map/soildp2_antigos/"
# files = [x for x in os.listdir(diretorio) if x.endswith(".nc")]

# def altera_um(file, fator,dy):

     
#      arquivo = file.split("/")[-1]
#      nome = arquivo.split(".")[0] 

#      if nome == "lzavin":
#          nome = "lzavin.nc"

        
#      dataset = xr.open_dataset(file)
#      dataset1 = dataset.copy()
#      dataset1[nome] = dataset[nome] * fator
     
#      os.remove(file)
#      dataset1.to_netcdf(file)
#      os.system(f"lisflood settings.xml")
     
#      result = pd.read_csv("./catch/out/chanqWin.tss",skiprows=3)
#      lista = []
#      indexer = result.columns.values[0]
#      for i in result[indexer]:
#          valor = i.split()[1]
#          lista.append(float(valor))
#      dy[f'{nome}_{fator}'] = lista

#      os.remove(file)
#      dataset.to_netcdf(file)
#      dy.to_csv(f"./csv_valores_.csv")
#      print(dy)
#      return f"sucesso para {nome}:{fator}"



# soildp = pd.DataFrame()
# for a in files:
#     file = f'{diretorio}{a}'
#     for y in [1,5,25]:
#         altera_um(file,y,soildp)
    
# dx = pd.read_csv("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/soildepth3_o.csv")    
# dx = pd.read_csv("/home/felipe.bortolletto/Downloads/DUI_Obras_intervencoes.csv",sep = ";",encoding = "ISO-8859-1")
