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
        # print(self.dataframe)
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
            "entrada": f"{self.IN_DIR}/{tipo}/",
            "saida":  f"{self.OUT_DIR}/maps/{tipo}/",
            "ON_OFF":False
            }
        self._dct = dct

    def define_ativos(self,nominal=None,tipos_alvo=None):
          self.nomes_paramns = pd.read_csv(f"{self.FILE_DIR}tabelas/fator_param_ranges.csv",index_col = 0)
          self.nomes_paramns["ON_OFF"] = True
          
          if nominal != None and tipos_alvo != None:
              for nom in nominal:
                  self.nomes_paramns.loc[self.nomes_paramns["ParameterName"] == nom,"ON_OFF"] = False
              for tipo in tipos_alvo:
                  self.nomes_paramns.loc[self.nomes_paramns["tipo"] == tipo,"ON_OFF"] = False
                  
          elif nominal != None:
              self.nomes_paramns["ON_OFF"] = ~self.nomes_paramns["tipo"].isin(nominal)
                  
          elif tipos_alvo != None:
              self.nomes_paramns["ON_OFF"] = ~self.nomes_paramns["tipo"].isin(tipos_alvo)
              
          self.nomes_paramns = self.nomes_paramns[self.nomes_paramns["ON_OFF"]==True]
          print("os seguintes parametros serão calibrados:")
          print(self.nomes_paramns)
          self.lower = self.nomes_paramns["MinValue"]
          self.upper = self.nomes_paramns["MaxValue"]
              
    def ler_parametros(self):
        self.nomes_paramns = pd.read_csv(f"{self.FILE_DIR}tabelas/fator_param_ranges.csv",index_col = 0)
        self.nomes_paramns["ON_OFF"] = True


    def ler_obs(self):
        df_loc = f"{self.FILE_DIR}tabelas/"

        obs = pd.read_csv(f"{df_loc}pm_vazao_obs.csv",index_col = 0,parse_dates=True)

        obs = obs["2013-01-01":"2023-04-07"]
        obs = obs.resample("D", closed='left', label='left').agg({'horleitura':(np.mean)})
        self._obs = obs

      
    def executa(self, arquivo_saida,r = 0.2,m = 1000):
        self.arquivo_saida = arquivo_saida
        self.resultados = pd.DataFrame() 
        
        self.xbest_f,self.fbest_f= self.dds(self.lower,self.upper,super().erro,r,m)
        self.plota()
        

        #%%
if __name__ == "__main__":
    
    temp = Calibrador()
    temp.inicializar()
    
    temp.reseta()
    temp.seta_melhores_parametros("./tabelas/resultados/plt_geral/12_9/primeiro teste serio.csv",skip = True)
    temp.reseta_for_the_best(nominal=["genua","lambda","ksat"],tipos_alvo = ["xml"])
    
    temp.define_ativos(nominal=["genua","lambda","ksat"],tipos_alvo = ["xml"])
    df_chuva = pd.read_csv("./tabelas/chuva_editada.csv",index_col = 0,parse_dates = True)
    df_chuva = df_chuva.media.to_frame()
    temp.define_nova_chuva(df_chuva)
    temp.executa("calibra_land_use",m =1500)
    
    temp2 = Calibrador()
    temp2.inicializar()
    
    temp2.reseta()
    temp2.seta_melhores_parametros("./tabelas/resultados/plt_geral/16_9/calibra_land_use.csv")
    temp2.reseta_for_the_best(nominal=["genua","lambda","ksat"],tipos_alvo = ["landuse"])
    
    temp2.define_ativos(nominal=["genua","lambda","ksat"],tipos_alvo = ["landuse"])
    df_chuva = pd.read_csv("./tabelas/chuva_editada.csv",index_col = 0,parse_dates = True)
    df_chuva = df_chuva.media.to_frame()
    temp2.define_nova_chuva(df_chuva)
    temp2.executa("calibra_xml",m =1000)
    

    