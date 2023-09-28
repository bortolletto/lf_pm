#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 10:51:35 2023

@author: felipe.bortolletto

filtro de kalman
"""

from pykalman import KalmanFilter
import numpy as np 
import pandas as pd 
# from pandas_dataread import data as pdr



sim = pd.read_csv(f"./chanqWin.tss",skiprows=3)
lista = []
for i in sim["1"]:
    valor = i.split()[1]
    lista.append(float(valor))

obs = pd.read_csv("./pm_vazao_obs.csv",index_col = 0,parse_dates = True)
obs = obs["2013":"2023-04-07"]
obs["sim"] = lista
obs = obs.fillna(obs.mean)
obs["tipo"] = "uno"
# obs_matriz = np.expand_dims(np.vstack([[obs["horleitura"]],
#                                        [np.ones(len(obs["sim"]))]]).T, axis=1) # Matriz das observações: retornos da BVSP e uma sequência de valores de unidade
# kf_r = KalmanFilter(initial_state_mean = [0,0], # Estado inicial do intercepto e coeficiente
#                     initial_state_covariance = np.ones((2, 2)), # Estado inicial da covariância (matriz identidade 2x2)
#                     transition_matrices = np.eye(2), # Matriz de transição do estado de t para t + 1 (matriz identidade 2x2)
#                     observation_matrices = obs_matriz) # Matriz das obs

# state_means, state_covs = kf_r.filter(obs.horleitura.values)

from darts.models import KalmanForecaster
from darts import TimeSeries
obs = obs.reset_index()
series_names = obs['sim'].unique()
train_series = TimeSeries.from_group_dataframe(obs, time_col='hordatahora', value_cols=["sim"],group_cols=["tipo"], freq='D', fill_missing_dates=True, fillna_value=obs.sim.mean())
valid = obs.loc[(obs['hordatahora'] >= '2013-01-01') & (obs['hordatahora'] < '2023-04-07')]
h = valid['hordatahora'].nunique()
preds = list()
for i, series in enumerate(train_series):
    model = KalmanForecaster(dim_x=1000)
    model.fit(series=series)
    p = model.predict(h).pd_dataframe().reset_index()
    p['Device Category'] = obs["sim"]
    preds.append(p)
# preds = pd.concat(preds, axis=0, ignore_index=True).rename(columns={'Sessions': 'Predicted'})



import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default='browser'
fig = go.Figure()
fig.add_trace(go.Scatter(x = preds.hordatahora,y = preds.sim,name = "sim"))
fig.add_trace(go.Scatter(x = preds.hordatahora,y = preds["Device Category"],name = "filtro"))
# ax[ax_].set_xlabel('Date')
# ax[ax_].set_ylabel('Sessions')
fig.show()