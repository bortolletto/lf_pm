#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 13:53:15 2023

@author: felipe.bortolletto
"""

import pandas as pd 
import xarray as xr
import numpy as np 
import os 

files = [x for x in os.listdir("./params_calibration/maps/landuse/") if x.endswith(".nc")]
saida = xr.open_dataset("./params_calibration/maps/outlets.nc")
pos = saida.band_data.where(saida.band_data == 1,drop = True)

for i in files:
    dx = xr.open_dataset(f"./params_calibration/maps/landuse/original/{i}")
    name_var = list(dx.variables)[-1]
    print(dx.loc[{'x':  pos.x, 'y': pos.y}][name_var].values[0][0])

    dx.loc[{'x':  pos.x, 'y': pos.y}] = 0.49640626  
    print(dx.loc[{'x':  pos.x, 'y': pos.y}][name_var].values[0][0])
    os.remove(f"../catch/maps/landuse/{i}")
    dx.to_netcdf(f"../catch/maps/landuse/{i}")
# df = pd.read_csv("/discolocal/felipe/git_pm/calibracao_manual/tabelas/fator_param_ranges.csv")






xr.open_dataset(f"../catch/maps/landuse/{i}").agua.values

# .selado.values
# /discolocal/felipe/lisf_pm/catch/maps/landuse/fracwater.nc