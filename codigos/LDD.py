#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 15:50:16 2023

@author: felipe.bortolletto

Precisamos refazer o arquivo de LDD
Assim como o Dem


"""



import xarray as xr
import os 
import numpy as np 


ldd = xr.open_dataset("../catch/maps/ec_ldd.nc")
rio = xr.open_dataset("/discolocal/felipe/git_pm/catch/maps/chanlength.nc")
# rio = rio.sel(band = 1)
# rio = rio.drop("band")
ld = ldd.band_data.values
rio= rio.chanlength.values

dem = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/elvstd.nc")
dem = np.array(dem.elvstd.values)

exiit = xr.open_dataset("../catch/maps/outlets.nc")
exiit = np.array(exiit.band_data.values)

# for i in ld:
#     print(i)

# print()
    
# for i in rio:
#     print(i)
    
# print()
    
# for i in dem:
#     print(i)
    
rio = np.array(rio)
ld = np.array(ld)

final = dem.copy()
ldd = ld.copy()

#dicionario para direçoes de ldd

dct_direc = {0: 8 ,
             1: 9,
             2: 6,
             3: 3,
             4: 2,
             5: 1,
             6: 4,
             7: 7,
             8: 5,
             }

#%%
for linha in range(len(dem)):
    for coluna in range(len(dem[0])):


        if linha == 0:        #linha superior
            if coluna ==0:
                S  = dem[linha +1][coluna]
                SL = dem[linha +1][coluna-1]
                L  = dem[linha][coluna+1]
                
                N  =  np.nan
                NL =  np.nan
                SO =  np.nan
                O  =  np.nan
                NO =  np.nan
            elif coluna == 19:
                S  = dem[linha +1][coluna]
                SO = dem[linha +1][coluna-1]
                O  = dem[linha ][coluna-1]
                
                NO = np.nan 
                N  = np.nan
                NL = np.nan
                L  = np.nan
                SL = np.nan
            else:
                L  = dem[linha][coluna+1]
                SL = dem[linha +1][coluna-1]
                S  = dem[linha +1][coluna]
                SO = dem[linha +1][coluna-1]
                O  = dem[linha ][coluna-1]
                
                N  =  np.nan
                NL =  np.nan
                NO =  np.nan
                
        elif linha == 11:   #linha de inferior
            if coluna ==0:
                N  = dem[linha -1][coluna]
                NL = dem[linha -1][coluna+1]
                L  = dem[linha][coluna+1]
                
                SL = np.nan
                S  = np.nan
                SO = np.nan
                O  = np.nan
                NO = np.nan
            elif coluna == 19:
                N  = dem[linha -1][coluna]
                O  = dem[linha ][coluna-1]
                NO = dem[linha -1][coluna-1]
                
                NL = np.nan
                L  = np.nan
                SL = np.nan
                S  = np.nan
                SO = np.nan
            else:
                N  = dem[linha -1][coluna]
                NL = dem[linha -1][coluna+1]
                L  = dem[linha][coluna+1]
                O  = dem[linha ][coluna-1]
                NO = dem[linha -1][coluna-1]
                
                SL = np.nan
                S  = np.nan
                SO = np.nan
        else:        #coluna esquerda
            if coluna ==0:
                N  = dem[linha -1][coluna]
                NL = dem[linha -1][coluna+1]
                L  = dem[linha][coluna+1]
                SL = dem[linha +1][coluna-1]
                S  = dem[linha +1][coluna]
                
                NO = np.nan
                SO = np.nan
                O  = np.nan
            elif coluna == 19:
                S  = dem[linha +1][coluna]
                SO = dem[linha +1][coluna-1]
                O  = dem[linha ][coluna-1]
                NO = dem[linha -1][coluna-1]
                N  = dem[linha -1][coluna]
                
                NL =  np.nan
                L  =  np.nan
                SL =  np.nan
            else:
                N  = dem[linha -1][coluna]
                NL = dem[linha -1][coluna+1]
                L  = dem[linha][coluna+1]
                SL = dem[linha +1][coluna-1]
                S  = dem[linha +1][coluna]
                SO = dem[linha +1][coluna-1]
                O  = dem[linha ][coluna-1]
                NO = dem[linha -1][coluna-1]
        dfinal = 0
        origem = dem[linha][coluna]
        cardiais = [N,NL,L,SL,S,SO,O,NO]
        contador = 0
        for i in cardiais:
            dif = abs(origem - i)
            if dif >= dfinal:
                dfinal = dif
                catch = contador
                # print(dfinal,contador)
            contador+=1
                # print(dfinal)
        if (origem < cardiais).all():
            contador = 8
        final[linha][coluna] = dfinal
        ldd[linha][coluna] = dct_direc[catch]


dem.elvstd.values = final
dem.to_netcdf("/discolocal/felipe/git_pm/catch/maps/changrads.nc")
# '''         
#   N  = dem[linha -1][coluna]
#   NL = dem[linha -1][coluna+1]
#   L  = dem[linha][coluna+1]
#   SL = dem[linha +1][coluna-1]
#   S  = dem[linha +1][coluna]
#   SO = dem[linha +1][coluna-1]
#   O  = dem[linha ][coluna-1]
#   NO = dem[linha -1][coluna-1]
#   '''
#%%

rio_test = rio.copy()

l0 = [32,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64]
l1 = [64,64,64,64,64,64,64,64,64,64,64,64,4,4,64,64,64,64,64,64]
l2 = [64,64,64,64,64,64,64,64,64,64,64,64,4,4,4,4,64,64,64,64]
l3 = [16,16,16,16,16,16,64,64,64,64,4,4,4,4,4,4,4,64,64,64]
l4 = [16,16,16,4,4,64,64,64,4,4,4,4,4,4,4,4,4,4,4,1]
l5 = [4,4,4,4,4,64,4,4,4,4,4,4,4,4,4,4,4,4,4,1]
l6 = [16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16]
l7 = [64,64,64,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16]
l8 = [16,16,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,1]
l9 = [6,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,1]
l10 = [16,16,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,1,1]
l11 = [16,16,4,64,64,4,4,4,4,4,4,64,64,64,64,4,4,4,4,1]

rio_test = np.array([l0,l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11])
# rio_test = np.array([l12,l11,l10,l9,l8,l7,l6,l5,l4,l3,l2,l1])
rio_test[rio_test ==1] = 6
rio_test[rio_test ==2] = 3
rio_test[rio_test ==4] = 2
rio_test[rio_test ==8] = 1
rio_test[rio_test ==16] = 4
rio_test[rio_test ==32] = 7
rio_test[rio_test ==64] = 8
rio_test[rio_test ==128] = 9

#%% exutorio:
    
exutorio = rio_test.copy()
for i in range(len(exutorio)):
    exutorio[i]=0
exutorio[7][0] = 1
#%%
ldd_file = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas copia/LDD/ec_ldd.tif")
ldd_file = ldd_file.sel(band=1)
ldd_file = ldd_file.drop("band")
# ldd_file = xr.open_dataset("../catch/maps/ec_ldd.nc")
ldd_file.band_data.values = rio_test
ldd_file = ldd_file.sortby(ldd_file.y,ascending = True)
os.remove("../catch/maps/ec_ldd.nc")
ldd_file.to_netcdf("../catch/maps/ec_ldd.nc")

#%%

exutorio_file = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas copia/LDD/ec_ldd.tif")
exutorio_file = exutorio_file.sel(band=1)
exutorio_file = exutorio_file.drop("band")

exutorio_file.band_data.values = [[0 for _ in range(len(exutorio_file.x))] for _ in range(len(exutorio_file.y))]
exutorio_file.band_data.values[6,0] = 1

exutorio_file = exutorio_file.sortby(exutorio_file.y,ascending = True)
os.remove("../catch/maps/outlets.nc")
exutorio_file.to_netcdf("../catch/maps/outlets.nc")
#%%

dem_file = xr.open_dataset("../catch/maps/elvstd.nc")


dem_file.elvstd.values = final[::-1]

os.remove("../catch/maps/elvstd.nc")



dem_file.to_netcdf("../catch/maps/elvstd.nc")

#%%

ldd_file = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/LDD/ec_ldd.tif")
ldd_file = ldd_file.sel(band=1)
ldd_file = ldd_file.drop("band")
ldd_file = ldd_file.sortby(ldd_file.y,ascending = True)
os.remove("../catch/maps/ec_ldd.nc")
ldd_file.to_netcdf("../catch/maps/ec_ldd.nc")
