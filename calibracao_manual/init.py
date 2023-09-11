#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 20:06:28 2023

@author: felipe
"""

# import os
import pandas as pd
# from pathlib import Path
import numpy as np
# import xarray as xr
from rotina import rodando
from funcionalidades import Funcionalidades

# import time
#%%
class Calibrador(rodando,Funcionalidades):
    
    def inicializar(self,tipos_alvo = None):
        self.ler_locais()
        self.cria_dct()
        self.ler_parametros()
        self.ler_obs()
        if tipos_alvo != None:
            
            self.define_ativos(tipos_alvo)
    def ler_locais(self):
        self.FILE_DIR = "./"
        self.IN_DIR = "./params_calibration"
        self.OUT_DIR ="../catch"
        self.SETTINGS_DIR = "../"

    def cria_dct(self):
        '''
        

        Returns
        -------
        Cria dicionario necessarios para localizacao de entradas e saidas, alem de outros parametros fundamentais. 

        '''
        
        self.dataframe = pd.read_csv(f"{self.FILE_DIR}tabelas/tabela.csv",index_col = 0)
        print(self.dataframe)
        dct = {}
        for nome ,tipo in zip(self.dataframe.index,self.dataframe.tipo):
            if tipo == "landuse":
                entrada = f"{self.IN_DIR}/{tipo}/"
                saida =  f"{self.OUT_DIR}/maps/{tipo}/"
            elif tipo == "soilhyd":
                entrada = f"{self.IN_DIR}/{tipo}/{nome}/"
                saida =  f"{self.OUT_DIR}/maps/{tipo}/"
            elif tipo == "table2map":
                entrada = f"{self.IN_DIR}/{tipo}/{nome}/"
                saida =  f"{self.OUT_DIR}/{tipo}/"
                
            dct[nome] =  {"tipo":tipo,
                         "entrada": entrada,
                         "saida":saida,
                         "ON_OFF" : True
                         }
            
        dct["cropgrpn"] = {
            "tipo":"table2map",
            "entrada": f"{self.OUT_DIR}/{tipo}/",
            "saida":  f"{self.OUT_DIR}/{tipo}/",
            "ON_OFF":False
            }
        self._dct = dct

    def define_ativos(self,tipos_alvo):
          
          for tipos in tipos_alvo:
              self.nomes_paramns.loc[self.nomes_paramns["tipo"] == tipos,"ON_OFF"] = False
    def ler_parametros(self):
        self.uper_lower = pd.read_csv(f"{self.FILE_DIR}tabelas/fator_param_ranges.csv",index_col = 0)
        self.lower = self.uper_lower["MinValue"]
        self.upper = self.uper_lower["MaxValue"]
        self.nomes_paramns = self.uper_lower["ParameterName"].to_frame()
        self.nomes_paramns["tipo"] = self.uper_lower["tipo"]
        self.nomes_paramns["ON_OFF"] = True
    
    def ler_obs(self):
        df_loc = f"{self.FILE_DIR}tabelas/"

        obs = pd.read_csv(f"{df_loc}pm_vazao_obs.csv",index_col = 0,parse_dates=True)

        obs = obs["2013-01-01":"2023-04-07"]
        obs = obs.resample("D", closed='left', label='left').agg({'horleitura':(np.mean)})
        self._obs = obs

      
    def executa(self, arquivo_saida,tipos_alvo = [],r = 0.2,m = 1000):
        self.arquivo_saida = arquivo_saida
        self.comparando_multiplos_anos = False
        self.resultados = pd.DataFrame()
 
        self.xbest_f,self.fbest_f= self.dds(self.lower,self.upper,super().erro,r,m)
        self.plota()
        
        self.resultados.set_index(self.nomes_paramns["ParameterName"],inplace =True)
        self.resultados = self.resultados.rename_axis(index={'ParameterName': 'F_obj:'})
        self.resultados.to_csv(f"{self.pasta }/{self.arquivo_saida}.csv")

        #%%
if __name__ == "__main__":
    
    temp = Calibrador()
    temp.inicializar()
    temp.reseta_for_the_best()
    df_chuva = pd.read_csv("./tabelas/chuva_editada.csv",index_col = 0,parse_dates = True)
    df_chuva = df_chuva.media.to_frame()
    temp.define_nova_chuva(df_chuva)
    temp.executa("primeiro teste serio",m =100)
    

    