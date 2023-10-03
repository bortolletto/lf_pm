#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:42:37 2023

@author: felipe.bortolletto
"""

import os 

import pandas as pd 
import xarray as xr

import numpy as np 
class Funcionalidades():
    
    def cria_super_csv(self):
        self._diretorios = [
            self.OUT_DIR +"/table2map",
                            self.OUT_DIR +"/meteo",
                            self.OUT_DIR +"/maps/soilhyd",
                            self.OUT_DIR +"/maps/landuse",
                            self.OUT_DIR +"/maps",
                            self.OUT_DIR +"/lai"
                            ] 
        self.df_estaticos = pd.DataFrame()
        self.df_estaticos = pd.DataFrame()
        self.df_estaticos = pd.DataFrame()
        
        first_meteo = True
        first_lai   = True
        first_estatico = True
        for _entrada in self._diretorios:
            files = [f for f in os.listdir(f"{_entrada}") if f.endswith(".nc")]
            for arquivo in files:
                entrada_temp = _entrada.split("/")[-1]
                dataset= xr.open_dataset(f"{_entrada}/{arquivo}")
                df = dataset.to_dataframe()
                if entrada_temp in ["meteo"]: #meteorologicos
                    if first_meteo:
                        self.df_meteo = pd.DataFrame(index = df.index)
                        first_meteo = False
                    if "spatial_ref" in df.columns:
                        df.drop(columns = ["spatial_ref"],inplace= True)
                    self.df_meteo = pd.merge(self.df_meteo,df,how = "inner",left_index=True,right_index=True)
                    
                elif entrada_temp in ["lai"]: #indices de area foliar
                    if "spatial_ref" in df.columns:
                        df.drop(columns = ["spatial_ref"],inplace= True)
                    if "band" in df.index.names:
                        df = df.droplevel('band')
                        
                    if first_lai:
                        self.df_lai = pd.DataFrame(index = df.index)
                        first_lai = False               
                    self.df_lai = pd.merge(self.df_lai,df,how = "inner",left_index=True,right_index=True)
                else: #diversos mapas estaticos
                    if "spatial_ref" in df.columns:
                        df.drop(columns = ["spatial_ref"],inplace= True)     
                    if "transverse_mercator" in df.columns:
                        df.drop(columns = ["transverse_mercator"],inplace= True) 
                    if "band_data" in df.columns:
                        df.rename(columns = {"band_data":arquivo},inplace = True)
                    if first_estatico:
                        self.df_estatico = pd.DataFrame(index = df.index)
                        first_estatico = False               
                    self.df_estatico = pd.merge(self.df_estatico,df,how = "inner",left_index=True,right_index=True)

        return self.df_estatico ,self.df_meteo , self.df_lai

    def reseta_for_the_best(self,nominal = None,tipos_alvo = None):
        
        self.resetando = pd.read_csv("./tabelas/fator_param_ranges.csv",index_col = 0)
        # print(self.resetando)
        self.resetando["ON_OFF"] = True

        if nominal != None and tipos_alvo != None:
            for nom in nominal:
                self.resetando.loc[self.resetando["ParameterName"] == nom,"ON_OFF"] = False
            for tipo in tipos_alvo:
                self.resetando.loc[self.resetando["tipo"] == tipo,"ON_OFF"] = False
                
        elif nominal != None:
            self.resetando["ON_OFF"] = ~self.resetando["tipo"].isin(nominal)
                
        elif tipos_alvo != None:
            self.resetando["ON_OFF"] = ~self.resetando["tipo"].isin(tipos_alvo)

        df_esperado = self.resetando.DefaultValue.to_frame()

        temp = df_esperado[df_esperado.columns.values[0]].values
        self.resetando["valores"] =temp
        settings_file = "../settings.xml"
        
        
        for variavel,nome  in zip( self.resetando.loc[self.resetando.tipo == "xml","valores"],self.resetando.loc[self.resetando.tipo == "xml","ParameterName"]) : 
                tipo = self.resetando.loc[self.resetando["ParameterName"] ==nome,"ON_OFF"].values[0]
                if tipo == False:
                    continue
                else:     
                    self.editar_valor_variavel(settings_file,2,nome,variavel)
                
        for variavel,nome  in zip( self.resetando.loc[self.resetando.tipo != "xml","valores"],self.resetando.loc[self.resetando.tipo != "xml","ParameterName"]) :         
             tipo = self.resetando.loc[self.resetando["ParameterName"] ==nome,"ON_OFF"].values[0]
             if tipo == False:
                 continue
             else:
                 self.inicia(nome,tipo,variavel)
                 self.manipular()
    def reseta(self):

        for chaves in self._dct.keys():
            entrada = self._dct[chaves]["entrada"]
            saida = self._dct[chaves]["saida"]
            self.files = [f for f in os.listdir(f"{entrada}") if f.endswith(".nc")]
            for arquivo in self.files:
                temp = xr.open_dataset(f"{entrada}{arquivo}")
                os.remove(f"{saida}{arquivo}")
                temp.to_netcdf(f"{saida}{arquivo}")
        print("Tudo volta a ser como ja foi...")
                    
    def plota_especifico(self,local_novo_plot,nome=None):
      df_esperado = pd.read_csv(local_novo_plot,index_col = 0)
      if len(df_esperado.columns) >1:
          df_esperado = df_esperado[df_esperado.columns[-1]].to_frame()
      
      temp = df_esperado[df_esperado.columns.values[0]].values
      self.erro(temp,substituir=True,recorta = False)
      if nome==None:
          self.arquivo_saida = local_novo_plot.split("/")[-1].split(".")[0]
      else:
          self.arquivo_saida = nome
      
      self.plota(plt_esp = True)           
          
          
    def define_nova_chuva(self,df_chuvas):
      base = xr.open_dataset("../catch/meteo/pr.nc")
      # data = pd.date_range(start="2013-01-03 00:00:00",end = "2023-04-09 00:00:00",freq = "D" )
      for coluna in df_chuvas.columns:
          
          temp = df_chuvas[coluna].to_frame()
          temp = temp["2013":"2023-04-07"]
          
 
          temp2 = base.copy()
          matrizes = []
         
          for _, row in temp.iterrows():
             matriz = np.full((12, 20), row[coluna])
             matrizes.append(matriz)
          temp2.pr.values = matrizes
          os.remove("../catch/meteo/pr.nc")
          temp2.to_netcdf("../catch/meteo/pr.nc")
     
    def seta_melhores_parametros(self,file=None,skip = False):
         
        if file ==None:
            file = "/discolocal/felipe/git_pm/calibracao_manual/tabelas/resultados/plt_geral/28_9/voltando as origens e funcionando.csv"
        else:
            file = file
        df = pd.read_csv("./tabelas/fator_param_ranges.csv",index_col = 0)
        dx = pd.read_csv(file)
        df.DefaultValue = dx[dx.columns.values[-1]]
        df.to_csv("./tabelas/fator_param_ranges.csv",index=True)
        # df = pd.read_csv("./tabelas/fator_param_ranges copia.csv")
        # if file ==None:
        #     file = "/home/felipe/Documentos/lf_pm/calibracao_manual/tabelas/melhor_resultado.csv"
            
        # dx = pd.read_csv(file)
        
        # if skip == False:
            
        #     for parametro in dx[dx.columns.values[0]]:
        #         df.loc[df.ParameterName == parametro,"DefaultValue"] = dx.loc[dx[dx.columns.values[0]]== parametro,dx.columns.values[-1]].values[0]
        #         print(df)
        # else:
        #     df.DefaultValue = dx[dx.columns[-1]].values

        # df.to_csv("./tabelas/fator_param_ranges.csv",index = True)
        
   #%%
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
           
    def calibra_humido(self,novo_ano,final_ano,r=0.02,m=400):
       caminho_arquivo = f"{self.SETTINGS_DIR}/settings.xml"  # Substitua pelo caminho correto
       self.ajustar_parametros_ano(caminho_arquivo, novo_ano,final_ano)
       self.ajustar_dimensao_temporal(novo_ano,final_ano)
       # self.reseta()
       # self.reseta_for_the_best()
       # self.define_ativos()
       self.executa("novo_umido metodologia antiga",r,m)
       
       df_esperado = pd.read_csv(self.place,index_col = 0)
       if len(df_esperado.columns) >1:
           df_esperado = df_esperado[df_esperado.columns[-1]].to_frame()
       
       temp = df_esperado[df_esperado.columns.values[0]].values
       
       self.ajustar_parametros_ano(caminho_arquivo, "2022","2022")
       self.ajustar_dimensao_temporal("2022","2022")
       
       self.erro(temp,substituir=True,recorta = False)
       
       self.arquivo_saida = "novo_humido"  
       self.plota(plt_esp = "humido")           
             
    def calibra_seco(self,novo_ano,final_ano,r=0.02,m=400):
        caminho_arquivo = f"{self.SETTINGS_DIR}/settings.xml"  # Substitua pelo caminho correto
        self.ajustar_parametros_ano(caminho_arquivo, novo_ano,final_ano)
        self.ajustar_dimensao_temporal(novo_ano,final_ano)
        # self.reseta()
        # self.reseta_for_the_best()
        # self.define_ativos()
        self.executa("novo seco metodologia antiga",r,m)
        df_esperado = pd.read_csv(self.place,index_col = 0)
        if len(df_esperado.columns) >1:
             df_esperado = df_esperado[df_esperado.columns[-1]].to_frame()
     
        temp = df_esperado[df_esperado.columns.values[0]].values
         
        self.ajustar_parametros_ano(caminho_arquivo, "2021","2021")
        self.ajustar_dimensao_temporal("2021","2021")
        
        self.erro(temp,substituir=True,recorta = False)
        
        self.arquivo_saida = "novo_seco"  
        self.plota(plt_esp = "seco")    
       
