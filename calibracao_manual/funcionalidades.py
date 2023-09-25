#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:42:37 2023

@author: felipe.bortolletto
"""

import os 
# from pathlib import Path
import pandas as pd 
import xarray as xr
import plotly.graph_objs as go
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
                # print(self.df_estatico)
        return self.df_estatico ,self.df_meteo , self.df_lai

    def reseta_for_the_best(self,nominal = None,tipos_alvo = None):
        
        self.resetando = pd.read_csv(f"./tabelas/fator_param_ranges.csv",index_col = 0)
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
        # print("parametros a seguir foram alterados:")
        # print(self.resetando)

        # self.resetando["ON_OFF"] = ~self.resetando["ON_OFF"].isin(tipos_alvo)
        # print(self.SETTINGS_DIR)
        settings_file = f"../settings.xml"
        
        
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
        # print(self._d1ct)
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
        df = pd.read_csv("./tabelas/fator_param_ranges.csv",index_col = 0)
        if file ==None:
            file = "/home/felipe/Documentos/lf_pm/calibracao_manual/tabelas/resultados/plt_geral/11_9/primeiro teste serio.csv"
        dx = pd.read_csv(file)
        
        if skip == False:
            for parametro in dx.ParameterName:
                df.loc[df.ParameterName == parametro,"DefaultValue"] = dx.loc[dx.ParameterName == parametro,dx.columns.values[-1]].values[0]
        else:
            df.DefaultValue = dx[dx.columns[-1]].values

        df.to_csv("./tabelas/fator_param_ranges.csv",index = True)
    # 
# if __name__ == "__main__":
    # temp = Funcionalidades()
    # temp.seta_melhores_parametros()
    
    # temp.reseta_for_the_best()
    # import xml.etree.ElementTree as ET
    
    # caminho_arquivo = "/discolocal/felipe/lisflood_pm/compara_anos.xml"  # Substitua pelo caminho correto
    
    # tree = ET.parse(caminho_arquivo)
    # root = tree.getroot()
    
    # novo_ano = "2017"  # Ano correspondente
    
    # for group_element in root.findall(".//group"):
    #     for textvar_element in group_element.findall('textvar'):
    #         var_nome = textvar_element.get('name')
    #         if var_nome == "CalendarDayStart" or var_nome == "timestepInit" or var_nome == "StepStart":
    #             textvar_element.set('value', novo_ano + "-01-01 00:00")
    #         elif var_nome == "StepEnd":
    #             if novo_ano == "2023":
    #                 textvar_element.set('value', "2023-07-04 00:00")
    #             else:
    #                 textvar_element.set('value', novo_ano + "-12-31 00:00")
    
    # tree.write(caminho_arquivo)