#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 17:29:57 2023

@author: felipe.bortolletto
"""

    
import numpy as np 
from osgeo import gdal
import xarray as xr

band_clay = gdal.Open("/discolocal/felipe/LF_pratico/lisflood_metros/lat.tif")
clay = band_clay.GetRasterBand(1)
c = clay.ReadAsArray()
error_value = clay.GetNoDataValue()


for i in range(len(c)):
    if i <=6:
        c[i] = 2
    elif i >=9:
        c[i] = 8
    else:
        c[i] = 4

base_nc = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood_metros/catch/maps/area.nc")
base_nc["area"] =(["y","x"],c)
base_nc.to_netcdf("/discolocal/felipe/LF_pratico/lisflood_metros/catch/maps/ec_ldd.nc")


verifica = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood_metros/catch/maps/soilhyd/thetas2_o.nc")
