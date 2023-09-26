#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 17:27:10 2023

@author: felipe
DDS NETCDF4


"""

from tqdm import tqdm
import pandas as pd
import numpy as np
import xarray as xr

df=xr.open_dataset('/home/felipe/Documentos/lf_pm/catch/maps/chan.nc')
dx = pd.read_csv("./tabelas/fator_param_ranges.csv",index_col = 0)
dx = dx.reset_index(drop = True)
lista = dx["DefaultValue"].to_list()[0:18]



for elemento in dx.index[18:]:
      print(elemento)
      Xmin = dx.loc[dx.index == elemento,"MinValue"].values[0]
      Xmax = dx.loc[dx.index == elemento,"MaxValue"].values[0]
      matriz = np.random.uniform(Xmin, Xmax, size=(len(df.x), len(df.y)))
      lista.append(matriz)         


def dds_nc(Xmin, Xmax, fobj, r=0.2, m=1000):
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
          print(i)
          Pi = 1 - np.log(i)/np.log(m)
          P = np.random.rand(len(Xmin))
          N = np.where(P < Pi)[0]
         
          if N.size == 0:
              N = [np.random.choice(ds)]
          # Passo 4
          Xnew = np.copy(Xbest)
          for j in N:
              if j <= 18:
                  
                  Xnew[j] = Xbest[j] + r*dX[j]*np.random.normal(0, 1)
                  if Xnew[j] < Xmin[j]:
                      Xnew[j] = Xmin[j] + (Xmin[j] - Xnew[j])
                      if Xnew[j] > Xmax[j]:
                          Xnew[j] = Xmin[j]
                  elif Xnew[j] > Xmax[j]:
                      Xnew[j] = Xmax[j] - (Xnew[j] - Xmax[j])
                      if Xnew[j] < Xmin[j]:
                          Xnew[j] = Xmax[j]
              else:
                  matriz = np.random.uniform(Xmin[j], Xmax[j], size=(20, 12))
                  Xnew[j] = matriz
          # Passo 5
          Fnew = fobj(Xnew)
          if Fnew <= Fbest:
              Fbest = Fnew
              Xbest = np.copy(Xnew)
              print(Fbest)
      # Fim
      return Xbest, Fbest 
  
    
 

                 
