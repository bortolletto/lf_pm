#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 16:44:23 2023

@author: felipe.bortolletto
"""
import pandas as pd 
import os
import xarray as xr
from osgeo import gdal
import numpy as np
from osgeo import gdal,gdal_array
#exutorio

band_clay = gdal.Open("/discolocal/felipe/LF_pratico/lisflood_metros/dados/base.nc")
clay = band_clay.GetRasterBand(1)
c = clay.ReadAsArray()
error_value = clay.GetNoDataValue()

for i in range(len(c)):
    c[i] = 0
c[8][1] = 1
# c[16][3] = 1
# c[20][3] = 1

driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lisflood_metros/dados/maps/exutorio.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.SetNoDataValue(error_value)

saida_band.WriteArray(c.astype(np.float32))
saida_dataset = None



#%% mapa de area
import numpy as np 
band_clay = gdal.Open("/discolocal/felipe/LF_pratico/lisflood_metros/dados/base.tif")
clay = band_clay.GetRasterBand(1)
c = clay.ReadAsArray()

for i in range(len(c)):
    c[i] = 1
driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lisflood_metros/dados/maps/area.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.WriteArray(c.astype(np.float32))
saida_dataset = None


#%% changrad
dem = gdal.Open("/discolocal/felipe/LF_pratico/lisflood_metros/dados/channel/elvstd.tif")
banda_dem= dem.GetRasterBand(1)
altura = banda_dem.ReadAsArray()

ldd = gdal.Open("/discolocal/felipe/LF_pratico/lisflood_metros/dados/channel/ec_ldd.tif")
banda_ldd = ldd.GetRasterBand(1)
direc = banda_ldd.ReadAsArray()

chanlen = gdal.Open("/discolocal/felipe/LF_pratico/lisflood_metros/dados/channel/chanlength.tif")
banda_len = chanlen.GetRasterBand(1)
leng = banda_len.ReadAsArray()


dicionario_direcoes = {
    8:[-1,0],
    6:[0,1],
    2:[+1,0],
    4:[0,-1],
    3:[+1,+1],
    7:[-1,-1],
    9:[-1,+1],
    1:[+1,-1],
    }
resultado = direc.copy()
changrad = direc.copy()

for y in range(len(direc)):
    y = int(y)
    for x in range(len(direc[y])):
        x = int(x)
        loclinha = dicionario_direcoes[direc[y][x]][0]
        loccoluna = dicionario_direcoes[direc[y][x]][1]
        alt1 = altura[y][x]
        try:
            alt2 = altura[y+loclinha][x+loccoluna]
        except:
            alt2 = 0
        valor = abs(alt1-alt2)/5000
        
        chanlengh = leng[y][x]
        
        if chanlengh >0:
            len_valor = abs(alt1-alt2)/chanlengh

        else:
            len_valor = 0
       
        print(alt1,alt2,chanlengh,"....",len_valor)
        print()    
        resultado[y][x] = valor
        changrad[y][x] = len_valor
        
driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lisflood_metros/dados/maps/changrad.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.WriteArray(changrad.astype(np.float32))
saida_dataset = None

driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lisflood_metros/dados/maps/gradient.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.WriteArray(resultado.astype(np.float32))
saida_dataset = None

#%%

lats = []

contador=1
for i in range(33):
    contador +=1
    lats.append(-25.23 - contador*0.045)
    
raster_dataset = gdal.Open("/discolocal/felipe/LF_pratico/lisflood_metros/dados/base.nc")
band = raster_dataset.GetRasterBand(1)
raster_data = band.ReadAsArray().astype(float)

for i in range(raster_data.shape[0]):
    raster_data[i] = lats[i]
    
driver = gdal.GetDriverByName('GTiff')

output_dataset = driver.Create("/discolocal/felipe/LF_pratico/lisflood_metros/dados/maps/lat.tif", raster_dataset.RasterXSize, raster_dataset.RasterYSize, 1, gdal_array.NumericTypeCodeToGDALTypeCode(raster_data.dtype))
output_dataset.SetGeoTransform(raster_dataset.GetGeoTransform())
output_dataset.SetProjection(raster_dataset.GetProjection())
output_band = output_dataset.GetRasterBand(1)
output_band.WriteArray(raster_data)
output_dataset = None
