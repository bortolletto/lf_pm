#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 16:09:54 2023

@author: felipe.bortolletto
calibracao e validacao lf


"""

import os
import pandas as pd 
import xarray as xr
import plotly.graph_objs as go
import numpy as np 
import datetime

class Calibracao_validacao():
    
  def ajustar_dimensao_temporal(self,novo_ano,ano_final):
      '''
      Função que ajusta o tempo dos dados temporais

      Parameters
      ----------
      novo_ano : int
          ano incial da rodada.
      ano_final : int
          ano final da rodada.
      '''
      origem = "./params_calibration/meteo/"
      destino = "../catch/meteo/"
      arquivos = [arquivo for arquivo in os.listdir(origem) if arquivo.endswith('.nc')]
      saida = [arquivo for arquivo in os.listdir(destino) if arquivo.endswith('.nc')]
      for arquivo in saida:
          df = xr.open_dataset(os.path.join(destino, arquivo))
          print(df)
      for arquivo in arquivos:
          caminho_arquivo = os.path.join(origem, arquivo)
          dataset = xr.open_dataset(caminho_arquivo)
          data_selecionada = dataset.sel(time=slice(f"{novo_ano}-01-01", f"{ano_final}-12-31"))
          dataset.close()
          
          novo_nome_arquivo = arquivo
          caminho_novo_arquivo = os.path.join(destino, novo_nome_arquivo)
          os.remove(caminho_novo_arquivo)
          data_selecionada.to_netcdf(caminho_novo_arquivo)
          print(f"Arquivo ajustado: {caminho_novo_arquivo}")
          
  def calibra_humido(self,novo_ano,final_ano,r=0.2,m=1000):
      caminho_arquivo = f"{self.SETTINGS_DIR}/compara_anos.xml"  # Substitua pelo caminho correto
      self.ajustar_parametros_ano(caminho_arquivo, novo_ano,final_ano)
      self.ajustar_dimensao_temporal(novo_ano,final_ano)
      self.reseta()
      # self.reseta_for_the_best()
      # self.define_ativos()
      self.executa(f"calibracao_humido_{novo_ano}:{final_ano}",r,m)
      
      df_esperado = pd.read_csv(self.place,index_col = 0)
      if len(df_esperado.columns) >1:
          df_esperado = df_esperado[df_esperado.columns[-1]].to_frame()
      
      temp = df_esperado[df_esperado.columns.values[0]].values
      
      self.ajustar_parametros_ano(caminho_arquivo, "2022","2022")
      self.ajustar_dimensao_temporal("2022","2022")
      
      self.erro(temp,substituir=True,recorta = False)
      
      self.arquivo_saida = f"humido_{novo_ano}_{final_ano}"  
      self.plota(plt_esp = "humido")           
            
  def calibra_seco(self,novo_ano,final_ano,r=0.2,m=1000):
       caminho_arquivo = f"{self.SETTINGS_DIR}/compara_anos.xml"  # Substitua pelo caminho correto
       self.ajustar_parametros_ano(caminho_arquivo, novo_ano,final_ano)
       self.ajustar_dimensao_temporal(novo_ano,final_ano)
       self.reseta()
       # self.reseta_for_the_best()
       # self.define_ativos()
       self.executa(f"calibracao_seco_{novo_ano}:{final_ano}",r,m)
       df_esperado = pd.read_csv(self.place,index_col = 0)
       if len(df_esperado.columns) >1:
            df_esperado = df_esperado[df_esperado.columns[-1]].to_frame()
    
       temp = df_esperado[df_esperado.columns.values[0]].values
        
       self.ajustar_parametros_ano(caminho_arquivo, "2022","2022")
       self.ajustar_dimensao_temporal("2022","2022")
       
       self.erro(temp,substituir=True,recorta = False)
       
       self.arquivo_saida = f"seco_{novo_ano}_{final_ano}"  
       self.plota(plt_esp = "seco")    
      
      
      
     