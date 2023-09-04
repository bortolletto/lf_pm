#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 16:46:20 2023

@author: felipe.bortolletto
Compara todos os resultados. :
    
"""

import plotly.graph_objs as go
import numpy as np
import pandas as pd
import datetime 
import os 
data_hoje = datetime.date.today()

def nse(predictions, targets):
    return (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))
            

df_loc = "../exutorios_catch/out/"
sim =  pd.read_csv(f'{df_loc}/chanqWin.tss',skiprows=9)

