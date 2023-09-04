#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 09:55:04 2023

@author: felipe.bortolletto

Arrumar os mapas de comprimento de canal/ maskara, o objetivo é encontrar saidas que contenham toda a bacia sem valores nulos.

"""


import xarray as xr 

df = xr.open_dataset("../catch/antigosa/chanlength.nc")

d =  df["chanlength"].where(df["chanlength"]>=1,other = 1)
 
df["chanlength"].values = d 
df.to_netcdf("../catch/maps/chanlength.nc")


# df = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/meteo/old/pr.nc")




#%%testes

xr_1 = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/out/len_1.nc")

xr_1000 = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/out/len_1000.nc")


list(xr_1.variables)
valores1 = xr_1.dis.values.sum()
valores1000 = xr_1000.dis.values.sum()

result = valores1  - valores1000
result.sum()


df = xr.open_dataset("../catch/maps/chanlength.nc")


#%% genualpha

df1 = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/antes modificados/genua3_o.nc")
df2 = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/antes modificados/genua3_f.nc")
df3 = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/antes modificados/genua2_o.nc")
df4 = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/antes modificados/genua2_f.nc")
df5 = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/antes modificados/genua1_o.nc")
df6 = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/antes modificados/genua1_f.nc")

lista = [df1,df2,df3,df4,df5,df6]
places = [
   "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/soilhyd/genua3_o.nc",
   "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/soilhyd/genua3_f.nc",
   "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/soilhyd/genua2_o.nc",
   "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/soilhyd/genua2_f.nc",
   "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/soilhyd/genua1_o.nc",
   "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/soilhyd/genua1_f.nc"
    ]
for i,z in zip (lista,places):
    temp = i.copy()
    
    nome = list(temp.variables)[-1]
    temp[nome]= temp[nome] * 1000
    test.where(temp[nome]<=0.055,other = 0.055)
    test.to_netcdf(z)
    
#%%

