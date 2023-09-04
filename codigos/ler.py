#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 10:23:57 2023

@author: felipe.bortolletto
"""
#arquivo que le mapas formato cama fload
#https://kpegion.github.io/Pangeo-at-AOES/examples/read-fortran-binary.html
import numpy as np
from array import array
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
fname='./rivlen/rivlen.bin'

#informacoes do arquivo .clt:
    
nlons=7200
nlats=3600
nvars=1
missing_value=-9999
neofs = 1 #caso de haver datas

lons = np.arange(7200)*-0.025 #tem q ser igual a 180 no final
lats = np.arange(3600)*-0.025 #tem q ser igual a 180 no final
lats = lats[::-1]
recl=(nlons*nlats+2)*4

data = np.zeros((neofs,nlats,nlons,nvars))

# Open file
luin = open(fname,'rb')

# Loop over all times
for e in range(neofs):

    # Loop over both variables
    for v in range(nvars):

        # Read in fortran record in bytes
        print(1)
        tmp=luin.read(recl)

        # Convert to single precision (real 32bit)
        tmp1=array('f',tmp)

        # Pull out data array (leaving behind fortran control records)for fortran sequential
        tmp2=tmp1

        # Create a 2d array (lat x lon) and store it in the data array
        data[e,:,:,v]=np.reshape(tmp2,(nlats,nlons))
z500=data[:,:,:,0]
#u250=data[:,:,:,1]



z500[z500<=missing_value]=np.nan

# 500 hPa Geopotential Height
z500_ds=xr.DataArray(z500,
                coords={'eofnum':[1],
                        'lat':lats,
                        'lon': lons},
                        dims=['eofnum','lat','lon'])
z500_ds=z500_ds.to_dataset(name='z500')

# z500_ds.to_dataframe().to_xarray().to_netcdf(path="/discolocal/felipe/aLisflood/glb_03min/rivlen/teste.nc")
#%%
luin = open('./rivlen/rivlen.bin','rb')
lat_s = open('./lonlat.bin','rb')

tmp=luin.read(recl)
tmp1=array('f',tmp)
tmp2 = lat_s.read(recl)
tmp2 = array('f',tmp2)
data[e,:,:,v] = np.reshape(tmp,(tmp2))

#%% recorta netcdf:
import rioxarray
import geopandas
from shapely.geometry import mapping
geodf = geopandas.read_file("/home/felipe.bortolletto/Documentos/teste.shp")

xds = rioxarray.open_rasterio("/discolocal/felipe/aLisflood/glb_03min/rivlen/len_river22.nc")
xds.rio.write_crs('EPSG:4326', inplace = True)
# clipped = xds.rio.clip(geodf.geometry,geodf.crs)
clipped = xds.rio.clip(geodf.geometry.apply(mapping), geodf.crs)
clipped.to_netcdf("/discolocal/felipe/aLisflood/glb_03min/rivlen/end.nc")
clipped.to_dataframe("/discolocal/felipe/aLisflood/glb_03min/rivlen/end.csv")

#%%
final = pd.DataFrame()
final["lat"] = 0
final["lon"] = 0
final["valor"] = 0
lista= []
lista_valores = []
lat = clipped.y.values[::-1]
lon = clipped.x.values[::-1]
valor = clipped.values[0][::-1]
contador = 0
for y in lat :
    
    contador2 = 0
    tmp = valor[contador]
    for x in lon :
        if contador%2 != 0:
            
            if contador2%2 !=0:
                
                lista.append((y,x,tmp[contador2]))
                lista_valores.append(tmp[contador2])
            else:
                pass
            contador2 +=1
        else:
            contador2 +=1
            pass
    contador +=1        
        
    
    
#%% lendo tiff original para passar para nova resolucao 




import rioxarray
import xarray as xr

from osgeo import gdal
#



land_use = rioxarray.open_rasterio("/discolocal/felipe/aLisflood/mapas/porto_amazonas/5km/dem.tif")
ds = gdal.Open("/discolocal/felipe/aLisflood/mapas/porto_amazonas/5km/dem.tif") 
xyz = gdal.Translate("./pixelarea.nc",ds)

df = xr.open_dataset("./pixelarea.nc").to_dataframe()

df["Band1"] = lista_valores

#df.to_xarray().to_netcdf("./chanlength.nc")


#%%

# df = xr.open_dataset("/discolocal/felipe/aLisflood/catch_lisflood/meteo/pr.nc").to_dataframe()

# df.index.set_names({ "data":"time"},inplace = True)
# df.to_xarray().to_netcdf("/discolocal/felipe/aLisflood/catch_lisflood/meteo/pr2.nc")

#%%
import numpy as np
from array import array
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

nlons = 21600
nlats = 10800
neofs = 1
nvars = 1
missing_value = -9999

lons = np.arange(21600)*0.0166666666666667 #tem q ser igual a 360 no final
lats = np.arange(10800)*0.0166666666666667 #tem q ser igual a 180 no final
# lons = lons -180
# lats = lats - 90
# 
lats = lats[::-1]
lons = lons[::-1]

recl=(nlons*nlats+2)*4

data = np.zeros((nlats,nlons,nvars))

luin = open("/discolocal/felipe/aLisflood/novo_lf/glb_01min/rivlen.bin","rb")


# for e in range(neofs):

    # Loop over both variables
for v in range(nvars):
    
    tmp = luin.read(recl)
    tmp1 = array("f",tmp)
    tmp2 = tmp1
    data[:,:,v]=np.reshape(tmp2,(nlats,nlons))



z500 = data[:,:,0]
z500[z500<=missing_value]=np.nan
lats = lats - 90
lons = lons - 180
lons = -lons
z500_ds=xr.DataArray(z500,
                coords={
                        'lat':lats,
                        'lon': lons},
                        dims=['lat','lon'])
z500_ds=z500_ds.to_dataset(name='z500')
z500_ds.to_netcdf("/discolocal/felipe/aLisflood/novo_lf/comprimento_de_canal_1minuto.nc")

#%%



#%%
import rioxarray
import geopandas
from shapely.geometry import mapping
geodf = geopandas.read_file("/discolocal/felipe/aLisflood/novo_lf/pcraster_format/channel/shape_maskara.shp")

xds = rioxarray.open_rasterio("/discolocal/felipe/aLisflood/novo_lf/glb_01min/inverso_subtraido.nc")
xds.rio.write_crs('EPSG:4326', inplace = True)
# clipped = xds.rio.clip(geodf.geometry,geodf.crs)
clipped = xds.rio.clip(geodf.geometry.apply(mapping), geodf.crs)


final = pd.DataFrame()
final["lat"] = 0
final["lon"] = 0
final["valor"] = 0
lista= []
lista_valores = []
lat = clipped.y.values[::-1]
lon = clipped.x.values[::-1]
valor = clipped.values[0][::-1]
contador = 0
for y in lat :
    
    contador2 = 0
    tmp = valor[contador]
    for x in lon :
        if contador%2 != 0:
            
            if contador2%2 !=0:
                
                lista.append((y,x,tmp[contador2]))
                lista_valores.append(tmp[contador2])
            else:
                pass
            contador2 +=1
        else:
            contador2 +=1
            pass
    contador +=1        
    
    
# clipped.to_netcdf("/discolocal/felipe/aLisflood/mapas/glb_03min/rivlen/teste--22.nc")
# clipped.to_dataframe("/discolocal/felipe/aLisflood/glb_03min/rivlen/end.csv")

#%%
def ler_fortran_data(nlons,nlats,neofs,nvars,missing_value,pixel_size,file):
    lons = np.arange(nlons)*pixel_size #tem q ser igual a 360 no final
    lats = np.arange(nlats)*pixel_size #tem q ser igual a 180 no final
    # lons = lons -180
    # lats = lats - 90
    # 
    lats = lats[::-1]
    lons = lons[::-1]

    recl=(nlons*nlats+2)*4

    data = np.zeros((nlats,nlons,nvars))

    luin = open(file,"rb")


    # for e in range(neofs):

        # Loop over both variables
    for v in range(nvars):
        
        tmp = luin.read(recl)
        tmp1 = array("f",tmp)
        tmp2 = tmp1
        data[:,:,v]=np.reshape(tmp2,(nlats,nlons))



    z500 = data[:,:,0]
    z500[z500<=missing_value]=np.nan
    lats = lats - 90
    lons = lons - 180
    lons = -lons
    z500_ds=xr.DataArray(z500,
                    coords={
                            'lat':lats,
                            'lon': lons},
                            dims=['lat','lon'])
    z500_ds=z500_ds.to_dataset(name='z500')
    # z500_ds.to_netcdf("/discolocal/felipe/aLisflood/novo_lf/comprimento_de_canal_1minuto.nc")
    return z500_ds

df = ler_fortran_data(21600, 10800, 1, 1, -9999, 0.01666667, "/discolocal/felipe/aLisflood/novo_lf/glb_01min/uparea_grid.bin")
df.to_netcdf("/discolocal/felipe/LF_pratico/lfmetros/chanel geometry/comprimento.map")
