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
    
    def inicializar(self):
        self.ler_locais()
        self.cria_dct()
        self.ler_parametros()
        self.ler_obs()
    def ler_locais(self):
        # self.FILE_DIR = Path(__file__).parent
        # self.IN_DIR = self.FILE_DIR / "params_calibration"
        # self.OUT_DIR = self.FILE_DIR.parent / "catch"
        # self.SETTINGS_DIR = self.FILE_DIR.parent 
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
        
        self.dataframe = pd.read_csv(f"{self.FILE_DIR}/tabelas/tabela.csv",index_col = 0)
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


    def ler_parametros(self):
        self.uper_lower = pd.read_csv(f"{self.FILE_DIR}/tabelas/fator_param_ranges.csv",index_col = 0)
        self.lower = self.uper_lower["MinValue"]
        self.upper = self.uper_lower["MaxValue"]
        self.nomes_paramns = self.uper_lower["ParameterName"].to_frame()
        self.nomes_paramns["tipo"] = self.uper_lower["tipo"]
        self.nomes_paramns["ON_OFF"] = True
        self.ler_obs()
    
    def ler_obs(self):
        df_loc = f"{self.FILE_DIR}/tabelas/"

        obs = pd.read_csv(f"{df_loc}pm_vazao_obs.csv",index_col = 0,parse_dates=True)

        obs = obs["2013-01-01":"2023-04-07"]
        obs = obs.resample("D", closed='left', label='left').agg({'horleitura':(np.mean)})
        self._obs = obs
    
    

    def define_ativos(self,tipos_alvo):
      
      for tipos in tipos_alvo:
          self.nomes_paramns.loc[self.nomes_paramns["tipo"] == tipos,"ON_OFF"] = False
      
    def executa(self, arquivo_saida,tipos_alvo = [],r = 0.2,m = 1000):
        self.arquivo_saida = arquivo_saida
        self.comparando_multiplos_anos = False
        #dataframe
        resultados = pd.DataFrame()
        self.define_ativos(tipos_alvo)
        self.xbest_f,self.fbest_f,resultados = self.dds(self.lower,self.upper,super().erro,resultados,r,m)
        self.plota()
        # print(self.nomes_params)
        self.resultados = resultados
        self.resultados.set_index(self.nomes_paramns["ParameterName"],inplace =True)
        self.resultados = self.resultados.rename_axis(index={'ParameterName': 'F_obj:'})
        resultados.to_csv(f"{self.pasta }/{self.arquivo_saida}.csv")

        #%%
if __name__ == "__main__":
    
    temp = Calibrador()
    temp.inicializar()
    temp.reseta_for_the_best()
    temp.executa("novo_test",["table2map"],r = 0.02,m = 500)
    # temp.executar_um_por_ano()
    
    # temp.compara_multiplos_anos()
    # temp.plota_especifico("/discolocal/felipe/lisflood_pm/calibracao_manual/tabelas/resultados/plt_geral/8_8/tablw2m.csv",["table2map"],nome = "novo_ldd")    
    # df_chuvas = pd.read_csv("/discolocal/felipe/lisflood_pm/chuva/possivel_chuva_final.csv",index_col=0,parse_dates = True)
    # # df_chuvas =  df_chuvas.resample("D").sum(min_count = 12)
    # df_chuvas = df_chuvas[["pr"]]
    # temp.define_nova_chuva(df_chuvas)
    # temp.executa("novo_test",["table2map"],r = 0.02,m = 4000)
   
    # temp.analisa_nova_chuva(df_chuvas)
    # # Coloque aqui o código que realiza a operação

    # 
    # temp.ativa_era5("ERA5")
   
    
    # fim_tempo = time.time()
    # tempo_total = fim_tempo - inicio_tempo

    # # with open('log.txt', 'a') as log_file:
    # #     log_file.write(f"Tempo total de execução: {tempo_total:.4f} segundos\n")
    # #     log_file.write("=" * 30 + "\n")  # Separador
        
    # temp.reseta()
    # temp.ativa_era5("simepar")
    # temp.executa("teste1_simepar",["table2map"],r = 0.02,m = 1000)
    
    # temp.reseta()
    # temp.ativa_era5("ERA5")
    # temp.executa("teste2_ERA5",["table2map"],r = 0.2,m = 1000)
    # temp.reseta()
    # temp.ativa_era5("simepar")
    # temp.executa("teste2_simepar",["table2map"],r = 0.2,m = 1000)
    
  
    # temp.analisa_area_da_curva()

    # temp.reseta()
    # temp.ativa_era5("ERA5")
    # temp.plota_especifico("/discolocal/felipe/lisflood_pm/calibracao_manual/tabelas/resultados/plt_geral/17_8/best.txt",["table2map"],nome = "kgb_last")    
    # temp.plota(arquivo_saida = "./rodadas_run_lf/2_colpleto")
    