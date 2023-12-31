#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 15:37:32 2023

@author: felipe.bortolletto

Programa com classe responsavel para rodar a calibração em si


"""

import xml.etree.ElementTree as ET
from tqdm import tqdm
import datetime 
import plotly.graph_objs as go
import os
import numpy as np 
import xarray as xr
import pandas as pd
from altera_xml import Altera_Xml
#%% Classe responsavel por executar os calculos


class rodando(Altera_Xml):
    
    def inicia(self,nome,tipo,fator):
       '''
       Parameters
       ----------
       nome : str
           Nome da variavel a ser alterada.
       tipo : str
           tipo de variavel a ser alterada ex: xml, table2map,etc.
       fator : float
           valor numerico que sera alterado a variavel.

       Returns
       -------
       Aqui os parametros e as variaveis serao lidas, para que possa-se calibrar o sistema

       '''      
       
       self._nome  = nome
       self._tipo  = tipo
       self._fator = fator
       
       self.diretorio_entrada = self._dct[self._nome]["entrada"]
       self.diretorio_saida = self._dct[self._nome]["saida"]
       self.files =[f for f in os.listdir(f"{self.diretorio_entrada}") if f.endswith(".nc")]

    def manipular(self):
        '''
        Função que altera o valor do nc        

        Returns
        -------
        None.


        '''
  
        for arquivo in self.files:
               self.dataset = xr.open_dataset(f"{self.diretorio_entrada}{arquivo}")
               self.name_var = list(self.dataset.variables)[-1]     
               self.dataset[self.name_var].values = [[self._fator for _ in range(len(self.dataset.x))] for _ in range(len(self.dataset.y))]
               os.remove(f"{self.diretorio_saida}{arquivo}")
               self.dataset.to_netcdf(f"{self.diretorio_saida}{arquivo}")
    def manipular_nc(self):
        '''
        Função que altera o valor do nc        

        Returns
        -------
        None.

        '''
        for arquivo in self.files:
               self.dataset = xr.open_dataset(f"{self.diretorio_entrada}{arquivo}")
               self.name_var = list(self.dataset.variables)[-1]  
               if  not isinstance(self._fator,float):
                   # print(self._fator)
                   self.dataset[self.name_var].values = self._fator
               else:
   
                   self.dataset[self.name_var].values = [[self._fator for _ in range(len(self.dataset.x))] for _ in range(len(self.dataset.y))]
               os.remove(f"{self.diretorio_saida}{arquivo}")
               self.dataset.to_netcdf(f"{self.diretorio_saida}{arquivo}")
 #%% 
 ######################## old dds ###############################
    def dds(self,Xmin, Xmax,X0, fobj, r=0.2, m=1000):
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

                  if hasattr(self, 'pasta') and isinstance(self.pasta, str):
                        "Felipe vc é demais , tome água e coma uma banana!"
                  else:
                      data_hoje = datetime.date.today()
                      local_pasta = f"{self.FILE_DIR}tabelas/resultados/plt_geral/"
                      self.pasta = f"{local_pasta}{data_hoje.day}_{data_hoje.month}/"
                      if not os.path.exists(self.pasta ):
                          os.makedirs(self.pasta )   
                  self.place = f"{self.pasta}/{self.arquivo_saida}.csv"
                  if not os.path.exists(self.place):
                      self.resultados = pd.DataFrame()
                      self.resultados.index = self.nomes_paramns.ParameterName
    
                      # print(self.nomes_paramns.DefaultValue)
                      self.resultados["default"] = self.nomes_paramns.DefaultValue.values
                      self.resultados.to_csv(self.place)          
                  
                  self.resultados = pd.read_csv(self.place,index_col = 0)
                  self.resultados[Fbest] = Xbest
                  self.resultados.to_csv(self.place)                 
          # Fim
          return Xbest, Fbest 
    
    ######################## old dds ###############################   
    #%%
    def nash(self,kge = "log"):
        if kge == False:
            self.df_merged = pd.merge(self.df,self._obs,left_index= True,right_index= True)
            targets = self.df_merged["horleitura"]
            predictions = self.df_merged["ls_dis"]
            self.nome_grafico = "nash"
            nash = np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)
            print(nash)
            return ( 1 - nash)
            # return np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)
        elif kge == True:
            import hydroeval as he
            self.df_merged = pd.merge(self.df,self._obs,left_index= True,right_index= True)
            targets = self.df_merged["horleitura"]
            predictions = self.df_merged["ls_dis"]
            kge, r, alpha, beta = he.evaluator(he.kge, predictions, targets)
            self.nome_grafico = "KGE"
            print(kge)
            return (1 - kge[0])
            # return kge[0]
        elif kge == "log":
            self.df_merged = pd.merge(self.df,self._obs,left_index= True,right_index= True)
            targets = self.df_merged["horleitura"]
            predictions = self.df_merged["ls_dis"]
            self.nome_grafico = "nash"
            nash = np.sum((np.log(targets)-np.log(predictions))**2)/np.sum((np.log(targets)-np.mean(np.log(targets)))**2)
            print(nash)
            return ( 1 - nash)

    def ler_saida(self):
        df_loc = f"{self.OUT_DIR}/out/"
        sim = pd.read_csv(f"{df_loc}/chanqWin.tss",skiprows=3)
        lista = []
        for i in sim["1"]:
            valor = i.split()[1]
            lista.append(float(valor))
        # ano_forcado = 2021
        if 367<=len(lista) <= 3000:
            data = pd.date_range(start=self.novo_ano,end = self.ano_final,freq = "D" ) #
        elif len(lista) <= 366:
            data = pd.date_range(start="2023-01-01 00:00:00",end = "2023-04-07 00:00:00",freq = "D" )
        else:
            data = pd.date_range(start="2013-01-03 00:00:00",end = "2023-04-09 00:00:00",freq = "D" )
        
        print(data)
        # data = data[:-1]
        self.df = pd.DataFrame(index = data)
        self.df["ls_dis"] = lista
        

    def plota(self,plt_esp = False):
        # df_loc = f"{self.OUT_DIR}/out/"
        local_pasta = f"{self.FILE_DIR}tabelas/resultados/plt_geral/"
        data_hoje = datetime.date.today()
        if plt_esp == False:
            self.pasta = f"{local_pasta}{data_hoje.day}_{data_hoje.month}/"
        elif plt_esp =="humido":
            self.pasta = "./tabelas/resultados/chuva/"
        elif plt_esp =="seco":
            self.pasta = "./tabelas/resultados/seco/"
        else:
            self.pasta = f"{self.FILE_DIR}/tabelas/resultados/plt_esp/"
        self.ler_saida()
        self.nash_value = self.nash()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = self.df_merged .index , y = self.df_merged .ls_dis,name = f"simulado {self.nome_grafico}: {self.nash_value}",marker_color = "red"))
        fig.add_trace(go.Scatter(x= self.df_merged .index,y=self.df_merged .horleitura,name = "obs", marker_color = "black"))
        if not os.path.exists(self.pasta ):
            os.makedirs(self.pasta )
            print(f"Pasta '{self.pasta }' criada com sucesso.")
        else:
            print(f"A pasta '{self.pasta }' já existe.")

        fig.write_html(f"{self.pasta }/{self.arquivo_saida}.html")
        print(f"figura {self.arquivo_saida} salva com sucesso!")   
        
  
        
    def erro(self,X):
        
        self.nomes_paramns["valores"]= X

        if hasattr(self,"settings") and self.settings != False :
            pass
        else:
            settings_file = f"{self.SETTINGS_DIR}/settings.xml"
            self.settings = settings_file
        settings_file = f"{self.SETTINGS_DIR}/settings.xml"
        for variavel,nome  in zip( self.nomes_paramns.loc[self.nomes_paramns.tipo == "xml","valores"],self.nomes_paramns.loc[self.nomes_paramns.tipo == "xml","ParameterName"]) : 
                   self.editar_valor_variavel(settings_file,2,nome,variavel)

        for variavel,nome  in zip( self.nomes_paramns.loc[self.nomes_paramns.tipo != "xml","valores"],self.nomes_paramns.loc[self.nomes_paramns.tipo != "xml","ParameterName"]) : 
     
                 tipo = self.nomes_paramns.loc[self.nomes_paramns["ParameterName"] ==nome,"ON_OFF"].values[0]
                 self.inicia(nome,tipo,variavel)
                 self.manipular()
        os.system(f"lisflood {settings_file}")

        self.ler_saida()
        self.nash_value = self.nash()
        # return self.nash_value
        if self.nash_value > 1 :
            return (1 - (-self.nash_value))
        else:
            return (1 - self.nash_value)
        
