#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 15:00:21 2023

@author: felipe.bortolletto
"""

import os 
import pandas as pd 
import numpy as np 
from tqdm import tqdm
import xarray as xr
dx = pd.read_csv("/discolocal/felipe/git_pm/calibracao_manual/tabelas/fator_param_ranges.csv",index_col = 0)

thetas = "./params_calibration/soilhyd/thetas"
thetar = "./params_calibration/soilhyd/thetar"
saida = "../catch/maps/soilhyd/"

lista = ["thetar3","thetar1","thetar2","thetar1_f","thetar2_f"]

files = [x for x in os.listdir(thetas)]
[files.append(x) for x in [y for y in os.listdir(thetar)]]

df = pd.DataFrame(columns = [dx.columns])
df["ParameterName"] = [x.split(".")[0] for x in files]
df["MinValue"] = [0 for x in range(len(files))]
df["MaxValue"] = [1 for x in range(len(files))]
df["DefaultValue"] = [0.48 for x in range(len(files))]
df["tipo"] = ["thetas" if x<9 else "thetar" for x in range(len(files))]

df["ON_OFF"] = ["ON" if x[0] in lista else "OFF" for x in df["ParameterName"].values ]

df.to_csv("/discolocal/felipe/git_pm/calibracao_manual/tabelas/fator_thetas.csv",index =True)

df = pd.read_csv("/discolocal/felipe/git_pm/validacao/resultados/calibra_thetas.csv",index_col = 0)

def dds(Xmin, Xmax,X0, fobj, r=0.2, m=1000):
      # Passo 1

      Xmin = np.asarray(Xmin)
      Xmax = np.asarray(Xmax)
      X0 = (Xmin + Xmax)/2
      D = len(Xmin)
      ds = [i for i in range(D)]
      dX = Xmax - Xmin
      # Passo 2
      I = np.arange(1, m+1, 1)
      Xbest = X0
      Fbest = fobj(Xbest)
      # Fbest =  abs(1 - fobj(X0))
      # Passo 3
      for i in tqdm(I):
          # print(i)
          Pi = 1 - np.log(i)/np.log(m)
          P = np.random.rand(len(Xmin))
          N = np.where(P < Pi)[0]
         
          if N.size == 0:
              N = [np.random.choice(ds)]
          # Passo 4
          Xnew = np.copy(Xbest)
          Xnew = np.array(Xbest, dtype=object)
          for j in N:
              # if j <= 18:
                  
                  Xnew[j] = Xbest[j] + r*dX[j]*np.random.normal(0, 1)
                  if Xnew[j] < Xmin[j]:
                      Xnew[j] = Xmin[j] + (Xmin[j] - Xnew[j])
                      if Xnew[j] > Xmax[j]:
                          Xnew[j] = Xmin[j]
                  elif Xnew[j] > Xmax[j]:
                      Xnew[j] = Xmax[j] - (Xnew[j] - Xmax[j])
                      if Xnew[j] < Xmin[j]:
                          Xnew[j] = Xmax[j]
              # else:
              #     matriz = np.random.uniform(Xmin[j], Xmax[j], size=(12, 20))

              #     Xnew[j] = matriz
          # Passo 5
          Fnew = fobj(Xnew)
          print(Fbest)
          if Fnew <= Fbest:
              Fbest = Fnew
              Xbest = np.copy(Xnew)
      # Fim
      return Xbest, Fbest 
  
def nse(predictions, targets):
    return (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))

  
def erro(X):
    
    df["DefaultValue"]= X
    settings_file = "../settings.xml"
    df.ON_OFF = [str(x) for x in df.ON_OFF]
    temp = df.loc[df.ON_OFF == "ON"]
    path_coleta = "/discolocal/felipe/git_pm/calibracao_manual/params_calibration/thetars_/"
    path_entrega = "/discolocal/felipe/git_pm/catch/maps/soilhyd/"
    for variavel,nome  in zip( temp.DefaultValue,temp.ParameterName) : 
             print(variavel,nome)
             dataset = xr.open_dataset(f"{path_coleta}{nome}.nc")
             name_var = list(dataset.variables)[-1] 
             dataset[name_var].values = [[variavel for _ in range(len(dataset.x))] for _ in range(len(dataset.y))]
             os.remove(f"{path_entrega}{nome}.nc")
             dataset.to_netcdf(f"{path_entrega}{nome}.nc")
    os.system(f"lisflood {settings_file}")
    
    df_loc = "../catch/out/"
    sim = pd.read_csv(f"{df_loc}/chanqWin.tss",skiprows=3)
    lista = []
    for i in sim["1"]:
        valor = i.split()[1]
        lista.append(float(valor))
    # ano_forcado = 2021
        
   
    obs = pd.read_csv("../calibracao_manual/tabelas/pm_vazao_obs.csv",index_col = 0,parse_dates=True)
    obs = obs["2013-01-01 00:00:00":"2015-12-31 00:00:00"]
    obs = obs.resample("D", closed='left', label='left').agg({'horleitura':(np.mean)})
    

    nash_value = nse(lista,obs["horleitura"])
    # return self.nash_value
    if nash_value > 1 :
        return (1 - (-nash_value))
    else:
        return (1 - nash_value)
    
X,F = dds(df.MinValue,df.MaxValue,df.DefaultValue,erro,r = 0.2,m = 600)
df.DefaultValue = F
df.to_csv("/discolocal/felipe/git_pm/validacao/resultados/calibra_thetas.csv",index = True)