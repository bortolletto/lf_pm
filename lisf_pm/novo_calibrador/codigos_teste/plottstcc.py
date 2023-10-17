#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 19:01:59 2023

@author: felipe
"""

import pandas as pd 
import xarray as xr
import plotly.io as pio
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

pio.renderers.default = 'browser'



chuva = xr.open_dataset("../../catch/meteo/pr.nc").to_dataframe()
era = xr.open_dataset("../../../../lf_pm/catch/meteo/chuvas/pr_era5_corrigido.nc").to_dataframe()
chuva = xr.open_dataset("../../../../lf_pm/catch/meteo/chuvas/idw_soma.nc").to_dataframe()

obs = pd.read_csv("../../tabelas/pm_vazao_obs.csv",index_col = 0,parse_dates=True)


try:
    era.drop(columns=["spatial_ref"],inplace=True)
    chuva.drop(columns=["spatial_ref"],inplace=True)
except:
    pass
era.rename(columns={"band_data":"era","pr":"era"},inplace = True)


chuva = chuva.groupby("time").mean()
era = era.groupby("time").mean()

# chuva = chuva.shift(-1)

df = pd.merge(chuva,era,left_index=True,right_index = True,how = "outer")
df = pd.merge(df,obs,left_index=True,right_index = True,how = "outer")
df = df["2013":]

for i in df.index.year.unique():
    temp = df[str(i)].copy()
    integral_A = np.trapz(temp["pr"].fillna(temp.pr.mean()))
    integral_B = np.trapz(temp["era"].fillna(temp["era"].mean()))
    print(f"{i}: diferença de água de {integral_A - integral_B}")
    
integral_A = np.trapz(df["pr"].fillna(df.pr.mean()))
integral_B = np.trapz(df["era"].fillna(df["era"].mean()))

print(f"total é igual a {abs(integral_A) - abs(integral_B)}")
    #%%
fig = go.Figure()

fig.add_trace(go.Scatter(x = df.index , y = df.pr,name = "pr",marker_color = "blue"))
fig.add_trace(go.Scatter(x = df.index , y = df.era,name = "era",marker_color = "red"))

fig.show()

# fig = make_subplots(specs = [[ { "secondary_y" : True}]])

# fig.add_trace(go.Scatter(x = df.index , y = df.pr,name = "pr",marker_color = "blue"),secondary_y=True)
# fig.add_trace(go.Scatter(x = df.index , y = df.era,name = "era",marker_color = "red"),secondary_y=True)

# fig.add_trace(go.Scatter(x = df.index , y = df.horleitura,name = "obs",marker_color = "black"),secondary_y=False)


# fig.update_layout(title = "periodo de 2013-2020")
# fig["layout"]["yaxis2"]["autorange"] = "reversed"
# fig.show()
 


