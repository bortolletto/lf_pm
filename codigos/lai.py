"""
Created on Mon May 22 14:45:36 2023

@author: felipe.bortolletto
PRograma para criar e recortar arquivo de indice de area foliar
"""

import pandas as pd 
import os
import xarray as xr
from osgeo import gdal



ds = gdal.Open("../dados/lai/lai_corrigido.tif")
gdal.Translate("../dados/lai/lai.nc",ds)
df = xr.open_dataset("../dados/lai/lai.nc").to_dataframe()    
data = pd.date_range(start="2017-01-01 00:00:00",end = "2018-01-01 00:00:00",freq = "D" )
lista = []
contador = 0
for x in data:
    contador +=1 
    if contador %10 == 0:
        lista.append(x)
        
    
df.drop(columns = ["transverse_mercator"],inplace= True)



contador = 0
first = True
for z,x in zip( df.columns,lista):

    temp = df[z].to_frame()
    temp.rename(columns = {z:"lai"},inplace=True)
    temp["time"] = x
    temp = temp.reset_index()
    temp.set_index(["time","y","x"],inplace =True)
    
    if first:
        final = temp.copy()
        first = False

    else:
        final = pd.concat([final,temp],axis = 0)
    print(x) 


laidataset = final.to_xarray().to_netcdf("../dados/lai/lai_final.nc")
os.system(f" gdalwarp -s_srs EPSG:31982 -t_srs EPSG:31982 -tr 5000.0 5000.0 -r average -te 607648.259 7044115.942 707648.259 7209115.942 -te_srs EPSG:31982 -of GTiff ../dados/lai/lai_final.nc ../dados/lai/lai_final.tif")
os.remove("../dados/lai/lai_final.nc")

#%% agora vamos criar os arquivos de fração de de indice de area foliar pela fração de solo respectivo.

# Abrir o arquivo TIFF do LAI
laidataset = gdal.Open('../dados/lai/lai_final.tif', gdal.GA_ReadOnly)
lai_bands = laidataset.RasterCount

base = gdal.Open("../dados/base.tif")
# Abrir o arquivo TIFF do tipo "forest"
forestdataset = gdal.Open('../dados/land_use/fracforest.tif', gdal.GA_ReadOnly)
forest_band = forestdataset.GetRasterBand(1)
forest = forest_band.ReadAsArray()

# Abrir o arquivo TIFF do tipo "irrigated"
irrigateddataset = gdal.Open('../dados/land_use/fracirrigated.tif', gdal.GA_ReadOnly)
irrigated_band = irrigateddataset.GetRasterBand(1)
irrigated = irrigated_band.ReadAsArray()

# Abrir o arquivo TIFF do tipo "other"
otherdataset = gdal.Open('../dados/land_use/fracother.tif', gdal.GA_ReadOnly)
other_band = otherdataset.GetRasterBand(1)
other = other_band.ReadAsArray()

# Listas contendo os arrays dos diferentes tipos
lista = [forest, irrigated, other]
lista_saida = ["../dados/lai/laif.tif", "../dados/lai/laii.tif", "../dados/lai/laio.tif"]

driver = gdal.GetDriverByName('GTiff')

for valor, output_file in zip(lista, lista_saida):
    output_dataset = driver.Create(output_file, base.RasterXSize, base.RasterYSize, lai_bands, forest_band.DataType)
    output_dataset.SetGeoTransform(base.GetGeoTransform())
    output_dataset.SetProjection(base.GetProjection())

    for band_index in range(1, lai_bands + 1):
        band = laidataset.GetRasterBand(band_index)
        lai = band.ReadAsArray()

        # Realizar a operação para a banda atual
        lai_output = lai * valor

        # Escrever a banda resultante no dataset de saída
        output_band = output_dataset.GetRasterBand(band_index)
        output_band.WriteArray(lai_output)

    output_dataset = None
os.remove("../dados/lai/lai_final.tif")


#%% salvamos agr no local correto com formato nc 

for output_file in lista_saida:
    data = xr.open_dataset(output_file)
    nome = output_file.split(".tif")[0].split("/")[3]
    data.to_netcdf(f"../catch/lai/{nome}.nc")