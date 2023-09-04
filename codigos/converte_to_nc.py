import pandas as pd 
import os
import xarray as xr
from osgeo import gdal

def convert_tif_netcdf(files_dir,to):
    # files_dir = "/discolocal/felipe/aLisflood/lisf_apresnt/catch_lisflood/arquivos que serao alterados/antigas resoc/mannings/novos/grad/"
    files = [f for f in os.listdir(files_dir) if f.endswith("tif")]
    # to =  "/discolocal/felipe/aLisflood/lisf_apresnt/catch_lisflood/arquivos que serao alterados/antigas resoc/mannings/novos/grad"
    
    for arquivo in files:
        print(arquivo)
        nome = arquivo.split(".")[0]
        
        ds = gdal.Open(f"{files_dir}/{arquivo}")
        
        xyz = gdal.Translate(f"{to}/{nome}.nc",ds)


    
    
# convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch/","/discolocal/felipe/LF_pratico/lfmetros/catch/")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/soilhidraulic/novos","/discolocal/felipe/LF_pratico/lfmetros/catch copia/maps/soilhyd")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/land_use/","/discolocal/felipe/LF_pratico/lfmetros/catch copia/maps/landuse")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/maps/","/discolocal/felipe/LF_pratico/lfmetros/catch copia/maps/channel/")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch/","/discolocal/felipe/LF_pratico/lfmetros/catch copia/")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/soilhidraulic/reprojetado/","/discolocal/felipe/LF_pratico/lfmetros/catch copia/maps/soilhyd/")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/ld_dependencis/","/discolocal/felipe/LF_pratico/lfmetros/catch copia/table2map")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/land_use_dependencies/soildep/resultados/","/discolocal/felipe/LF_pratico/lfmetros/catch copia/table2map/")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch/maps/channel/","/discolocal/felipe/LF_pratico/lfmetros/catch copia/maps/channel/")
convert_tif_netcdf("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/gradientes/","/discolocal/felipe/LF_pratico/lfmetros/catch copia/maps/channel/")

#%%
file_dir = "/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/soilhidraulic/"
files = [f for f in os.listdir(file_dir) if f.endswith(".tif")]

for arquivo in files:
    nome = arquivo.split(".")[0]
    print(nome)
    os.system(f" gdalwarp -s_srs EPSG:31982 -t_srs EPSG:31982 -tr 5000.0 5000.0 -r average -te 607648.259 7044115.942 707648.259 7209115.942 -te_srs EPSG:31982 -of GTiff {file_dir}{arquivo} {file_dir}/reprojetado/{nome}.tif")



#%% converte os parametros para f e o


file_dir = "/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/soilhidraulic/reprojetado/"
files = [f for f in os.listdir(file_dir) if f.endswith(".tif")]
for i in files:
    
    
    nome = i.split(".")[0]
    band_clay = gdal.Open(f"{file_dir}{i}")
    clay = band_clay.GetRasterBand(1)
    c = clay.ReadAsArray()
    error_value = clay.GetNoDataValue()
    
    band_floresta = gdal.Open("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/land_use/tipo_forest.tif")
    floresta = band_floresta.GetRasterBand(1)
    f = floresta.ReadAsArray()
    f_error = floresta.GetNoDataValue()
    
    banda_outros = gdal.Open("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/land_use/bare_reducao_75cento.tif")
    outros = banda_outros.GetRasterBand(1)
    o = outros.ReadAsArray()
    o_error = outros.GetNoDataValue()
    
    resultadof = c * f
    resultadoo = c * (1-f)
    
    pixels_no_data = np.where(c == error_value)
    resultadof[pixels_no_data] = error_value
    resultadoo[pixels_no_data] = error_value
    
    for z in range(2):
        if z == 0:
            saida_path = f"/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/soilhidraulic/novos/{nome}_f"
            resultado = resultadof
        if z == 1:
            saida_path = f"/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/soilhidraulic/novos/{nome}_o"
            resultado = resultadoo    

        driver = gdal.GetDriverByName('GTiff')
        saida_dataset = driver.Create(saida_path, band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
        saida_dataset.SetProjection(band_clay.GetProjection())
        saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())
        
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band.SetNoDataValue(error_value)
        
        saida_band.WriteArray(resultado.astype(np.float32))
        saida_dataset = None
    

exutorio = pd.DataFrame()
exutorio["lat"] = [-26.110019999999999,-25.548220000000001,-25.946629999999999]
exutorio["lon"] = [-49.802700000000002,-49.888430000000000,-49.797220000000003]
exutorio.to_csv("/discolocal/felipe/LF_pratico/lfmetros/catch/pontos_exutorio.csv")

#%% exutorio:

band_clay = gdal.Open("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/maps/dem.tif")
clay = band_clay.GetRasterBand(1)
c = clay.ReadAsArray()
error_value = clay.GetNoDataValue()

for i in range(len(c)):
    c[i] = 0
c[8][1] = 1
# c[16][3] = 1
# c[20][3] = 1

driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lfmetros/catch/exutorio.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.SetNoDataValue(error_value)

saida_band.WriteArray(c.astype(np.float32))
saida_dataset = None
#%% mapa de area
import numpy as np 
band_clay = gdal.Open("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/maps/dem.tif")
clay = band_clay.GetRasterBand(1)
c = clay.ReadAsArray()

for i in range(len(c)):
    c[i] = 1
driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lfmetros/catch_lisflood/maps/area.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.WriteArray(c.astype(np.float32))
saida_dataset = None

#%%

#slop gradiente geral

dem = gdal.Open("/discolocal/felipe/LF_pratico/lfmetros/chanel geometry/dem.tif")
banda_dem= dem.GetRasterBand(1)
altura = banda_dem.ReadAsArray()

ldd = gdal.Open("/discolocal/felipe/LF_pratico/lfmetros/chanel geometry/ec_ldd.tif")
banda_ldd = ldd.GetRasterBand(1)
direc = banda_ldd.ReadAsArray()

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
resultado = direc
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
        print(abs(alt1-alt2)/5000)    
        resultado[y][x] = valor
driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lfmetros/chanel geometry/slop.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.WriteArray(resultado.astype(np.float32))
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
resultado = direc
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
        
        len_valor = abs(alt1-alt2)/chanlengh
        
        resultado[y][x] = valor
        changrad[y][x] = len_valor
        
driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lisflood_metros/catch/maps/changrad.nc", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.WriteArray(changrad.astype(np.float32))
saida_dataset = None

driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lisflood_metros/catch/maps/gradient.nc", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.WriteArray(resultado.astype(np.float32))
saida_dataset = None


#%% arrumando ldd:
'''
tenho duvidas sobre o ldd map 
assimm irei refazelo de modo que converja para o rio sempre. 
Para issoa primeira abordagem foi testada tivemos uma diferença na vazao significativa 

e uma segunda sera implementada
'''

import numpy as np 
band_clay = gdal.Open("/discolocal/felipe/LF_pratico/lfmetros/chanel geometry/ec_ldd.tif")
clay = band_clay.GetRasterBand(1)
c = clay.ReadAsArray()
error_value = clay.GetNoDataValue()

for i in range(len(c)):
    if i <=6:
        c[i] = 2
    elif i >6:
        c[i] = 8
# c[8][1] = 1
# c[16][3] = 1
# c[20][3] = 1

driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lfmetros/catch/ldd.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.SetNoDataValue(error_value)

saida_band.WriteArray(c.astype(np.float32))
saida_dataset = None
#%%
# Sucesso ! Vamos para a segunda alternativa:
    
import numpy as np 
from osgeo import gdal


band_clay = gdal.Open("/discolocal/felipe/LF_pratico/lfmetros/chanel geometry/ec_ldd.tif")
clay = band_clay.GetRasterBand(1)
c = clay.ReadAsArray()
error_value = clay.GetNoDataValue()


for i in range(len(c)):
    if i <=6:
        c[i] = 2
    elif i >9:
        c[i] = 8
    # else:
    #     c[i] = 4
driver = gdal.GetDriverByName('GTiff')
saida_dataset = driver.Create("/discolocal/felipe/LF_pratico/lfmetros/catch/ldd.tif", band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
saida_dataset.SetProjection(band_clay.GetProjection())
saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())

saida_band = saida_dataset.GetRasterBand(1)
saida_band.SetNoDataValue(error_value)

saida_band.WriteArray(c.astype(np.float32))
saida_dataset = None