#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 18 15:51:12 2023

@author: felipe.bortolletto
"""
import os
import xarray as xr
from osgeo import gdal
import pandas as pd
import numpy as np 
from numpy import inf
'''
Programa com finalidade de transformar e calcular os parametros de dependencia do solo para o lisflood
É necessario ter os arquivos de tipo de solo classificados e ponderados, as entradas tambem funcionam com a fração de cada tipo de solo
'''

#setamos os diretorios e lemos o arquivo de profundidade de solo
diretorios = [
"../dados/land_use_dependencies/agro/final/", # agro
"../dados/land_use_dependencies/other/final/", # outros
"../dados/land_use_dependencies/floresta/final/" # floresta
    ]
base = gdal.Open('../dados/land_use_dependencies/soildep/BDTICM_M_5000m_mm.tif')
base_nc = base.GetRasterBand(1)
base_values = base_nc.ReadAsArray()

tipos = ["i","o","f"]
#carregamos dados e parametros q seram utilizados

dados = pd.read_csv("../dados/land_use_dependencies/Lisfloodd - copernicus.csv",index_col = 1)



for  files_dir,tipo, in zip(diretorios,tipos):
    files = [f for f in os.listdir(files_dir) if f.endswith(".tif")]

    contador = 0
    crop_he = []
    crop_coef = []
    root_deep = []
    group_number = []
    mannings = []
    fraction = []
    
    

    for arquivo in files:

        dados_tif = gdal.Open(f"{files_dir}{arquivo}")
        dados_band = dados_tif.GetRasterBand(1)
        result = dados_band.ReadAsArray()
        no_data = dados_band.GetNoDataValue()

        # print(np.min(result))
        
        nome = arquivo.split(".")[0]
        kc = float(dados.loc[dados.index == int(nome),"crop coef"].values[0].replace(",","."))
        he = float(dados.loc[dados.index == int(nome),"height"].values[0].replace(",","."))
        gn = float(dados.loc[dados.index == int(nome),"crop gruop"].values[0])
        man = float(dados.loc[dados.index == int(nome),"manning"].values[0].replace(",","."))
        root = float(dados.loc[dados.index == int(nome),"croop root"].values[0].replace(",","."))
        
        crop_he.append(result * he)
        
        crop_coef.append(result * kc * he)
        
        root_deep.append(result * root)
        
        group_number.append(result * gn)
        
        mannings.append(result * man)
        
        fraction.append(result)

    kc      = sum(crop_coef)/sum(crop_he) 
    h    = sum(crop_he)   / sum(fraction) 
    r    = sum(root_deep)   / sum(fraction) 
    kg  = sum(group_number)/ sum(fraction) 
    km   = sum(mannings)    / sum(fraction) 
    
    labels = ["cropcoef_","crop height","crop root depth","cropgrpn_","mannings_"]
    resultados = [kc,h,r,kg,km]
    contador = 0
    for valores,titulo in zip(resultados,labels):
        for i in range(len(valores)):
            valores[i] = np.nan_to_num(valores[i],np.min(valores[i]))
            if titulo == "cropgrpn_":
                moda = np.max(valores[i])
                valores[i] = np.where(valores[i] == 0,moda,valores[i])
                # valores[i] = [round(f) for f in valores[i]]
                valores[i] = [round(f)  for f in valores[i]]
                
            contador+=1
           
    for valores,titulo  in zip (resultados,labels):
        print()
        print(f"{titulo}:")
        print(f"max : {np.max(valores)}")
        print(f"min : {np.min(valores)}")
        valores = np.nan_to_num(valores,nan = no_data)
        
        if titulo == "crop root depth" or titulo =="crop height":
            saida_path = f"../dados/land_use_dependencies/resultado/cr_ch/{titulo}{tipo}.tif"
        else:
            saida_path = f"../dados/land_use_dependencies/resultado/{titulo}{tipo}.tif"
        driver = gdal.GetDriverByName('GTiff')
        saida_dataset = driver.Create(saida_path, base.RasterXSize, base.RasterYSize, 1, gdal.GDT_Float64)
        saida_dataset.SetProjection(base.GetProjection())
        saida_dataset.SetGeoTransform(base.GetGeoTransform())
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band.SetNoDataValue(no_data)
        saida_band.WriteArray(valores.astype(np.float32))
        saida_dataset = None
        

#%%  
'''
agora faremos os mapas de soildepth
lembrando:
    base = gdal.Open('./soildep/BDTICM_M_5000m_mm.tif')
    base_nc = base.GetRasterBand(1)
    base_values = base_nc.ReadAsArray()
    
'''

for tipo in tipos:
    if tipo == "f":
        base = gdal.Open('../dados/land_use_dependencies/resultado/cr_ch/crop root depthf.tif')
        base_nc = base.GetRasterBand(1)
        root = base_nc.ReadAsArray()
        
    elif tipo =="i":
        base = gdal.Open('../dados/land_use_dependencies/resultado/cr_ch/crop root depthi.tif')
        base_nc = base.GetRasterBand(1)
        root= base_nc.ReadAsArray()
        
    elif tipo == "o":
        base = gdal.Open('../dados/land_use_dependencies/resultado/cr_ch/crop root deptho.tif')
        base_nc = base.GetRasterBand(1)
        root = base_nc.ReadAsArray()

#ambos em mm , logo passamos a profundidade das raizes para metros
    
    root = root *1000
    
####### soildpeth1 ##########################################
    soildpeth1 = base_values.copy()
    for i in range(len(soildpeth1)):
        soildpeth1[i] = 50

####### soildpeth2 ##########################################
    soildpeth2 = np.minimum(root,base_values -300 - 50)
    soildpeth2 = np.where(soildpeth2 <= 50 ,50,soildpeth2)
    
####### soildpeth3 ##########################################
    
    soildpeth3 = base_values - (soildpeth2 + soildpeth1)

#salvamos agora:
    nomes = ["soildepth1_","soildepth2_","soildepth3_"]
    for solos,titulo in zip([soildpeth1,soildpeth2,soildpeth3],nomes):
        
        solos = np.nan_to_num(solos,nan = no_data)
        saida_path = f"../dados/land_use_dependencies/resultado/{titulo}{tipo}.tif"
        driver = gdal.GetDriverByName('GTiff')
        saida_dataset = driver.Create(saida_path, base.RasterXSize, base.RasterYSize, 1, gdal.GDT_Float64)
        saida_dataset.SetProjection(base.GetProjection())
        saida_dataset.SetGeoTransform(base.GetGeoTransform())
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band.SetNoDataValue(no_data)
        saida_band.WriteArray(solos.astype(np.float32))
        saida_dataset = None

#%%
final = [f for f in os.listdir("../dados/land_use_dependencies/resultado") if f.endswith("tif")]
for output_file in final:
    data = xr.open_dataset(f"../dados/land_use_dependencies/resultado/{output_file}")
    nome = output_file.split(".tif")[0]
    data.to_netcdf(f"../catch/table2map/{nome}.nc")
        
 

#%%






