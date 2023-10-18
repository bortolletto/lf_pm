#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 08:28:11 2023

@author: felipe.bortolletto
"""

import pandas as pd 
import xarray as xr
import os

def cria_super_csv():
    
    diretorios = [
    "../catch/table2map",
    "../catch/meteo",
    "../catch/maps/soilhyd",
    "../catch/maps/landuse",
    "../catch/maps",
    "../catch/lai"
                        ]    
    first_meteo = True
    first_lai   = True
    first_estatico = True
    for _entrada in diretorios:
        files = [f for f in os.listdir(f"{_entrada}") if f.endswith(".nc")]
        for arquivo in files:
            entrada_temp = _entrada.split("/")[-1]
            dataset= xr.open_dataset(f"{_entrada}/{arquivo}")
            df = dataset.to_dataframe()
            if entrada_temp in ["meteo"]: #meteorologicos
                if first_meteo:
                    df_meteo = pd.DataFrame(index = df.index)
                    first_meteo = False
                if "spatial_ref" in df.columns:
                    df.drop(columns = ["spatial_ref"],inplace= True)
                df_meteo = pd.merge(df_meteo,df,how = "inner",left_index=True,right_index=True)
                
            elif entrada_temp in ["lai"]: #indices de area foliar
                if "spatial_ref" in df.columns:
                    df.drop(columns = ["spatial_ref"],inplace= True)
                if "band" in df.index.names:
                    df = df.droplevel('band')
                    
                if first_lai:
                    df_lai = pd.DataFrame(index = df.index)
                    first_lai = False               
                df_lai = pd.merge(df_lai,df,how = "inner",left_index=True,right_index=True)
            else: #diversos mapas estaticos
                if "spatial_ref" in df.columns:
                    df.drop(columns = ["spatial_ref"],inplace= True)     
                if "transverse_mercator" in df.columns:
                    df.drop(columns = ["transverse_mercator"],inplace= True) 
                if "band_data" in df.columns:
                    df.rename(columns = {"band_data":arquivo},inplace = True)
                if first_estatico:
                    df_estatico = pd.DataFrame(index = df.index)
                    first_estatico = False               
                df_estatico = pd.merge(df_estatico,df,how = "inner",left_index=True,right_index=True)

    return df_estatico ,df_meteo , df_lai


estaticos,meteo,lai = cria_super_csv()