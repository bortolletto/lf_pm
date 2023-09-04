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

    def reseta_for_the_best(self,nome=None):
        self.define_ativos(["table2map"])
        local_novo_plot = "/discolocal/felipe/lisflood_pm/calibracao_manual/tabelas/resultados/plt_geral/8_8/tablw2m.csv"
        df_esperado = pd.read_csv(local_novo_plot,index_col = 0)
        if len(df_esperado.columns) >1:
            df_esperado = df_esperado[df_esperado.columns[-1]].to_frame()
        for colunas in df_esperado:
            temp = df_esperado[colunas].values
            self.nomes_paramns["valores"]= temp
            print(self.nomes_paramns)
            settings_file1 =  f"{self.SETTINGS_DIR}/compara_anos.xml"
            settings_file2 = f"{self.SETTINGS_DIR}/settings.xml"
            for settings_file in [settings_file1,settings_file2]:

                for variavel,nome  in zip( self.nomes_paramns.loc[self.nomes_paramns.tipo == "xml","valores"],self.nomes_paramns.loc[self.nomes_paramns.tipo == "xml","ParameterName"]) : 
                    self.editar_valor_variavel(settings_file,2,nome,variavel)
                
                for variavel,nome  in zip( self.nomes_paramns.loc[self.nomes_paramns.tipo != "xml","valores"],self.nomes_paramns.loc[self.nomes_paramns.tipo != "xml","ParameterName"]) : 
                
                     tipo = self.nomes_paramns.loc[self.nomes_paramns["ParameterName"] ==nome,"ON_OFF"].values[0]
                     if tipo == False:
                         continue
                     else:
                         self.inicia(nome,tipo,variavel)
                         # self.Open()
                         self.manipular()

    def reseta(self):

                for chaves in self._dct.keys():

                  entrada = self._dct[chaves]["entrada"]
                  
                  saida = self._dct[chaves]["saida"]

                  self.files = [f for f in os.listdir(f"{entrada}") if f.endswith(".nc")]
                  for arquivo in self.files:

                    temp = xr.open_dataset(f"{entrada}{arquivo}")
                    # temp = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/pm_calibracao_paramns/calibracao_manual/params_calibration/table2map/soildepth3/soildepth3_o.nc")
                   
                    os.remove(f"{saida}{arquivo}")
                    temp.to_netcdf(f"{saida}{arquivo}")
                print("Tudo volta a ser como ja foi...")
                    
    def plota_especifico(self,local_novo_plot,out_in = [],nome=None):
      self.comparando_multiplos_anos = False
      self.define_ativos(out_in)
      df_esperado = pd.read_csv(local_novo_plot,index_col = 0)
      if len(df_esperado.columns) >1:
          df_esperado = df_esperado[df_esperado.columns[-1]].to_frame()
      for colunas in df_esperado:
          temp = df_esperado[colunas].values
          self.erro(temp,substituir=True,recorta = False)
          if nome==None:
              self.arquivo_saida = local_novo_plot.split("/")[-1].split(".")[0]
          else:
              self.arquivo_saida = nome
          self.plota(plt_esp = True)           
          
          
    def analise_sensibilidade(self,fator):
        lista = ["maps",
        "table2map",
        "meteo",
        "lai",
        # "maps/landuse",
        "maps/soilhyd"
        ]
        final = pd.DataFrame()
        for local in lista:
            diretorio = f"{self.OUT_DIR}/{local}"
            files = [x for x in os.listdir(diretorio) if x.endswith(".nc")]
            print(files)
            for arquivo in files:
                nome = arquivo.split(".")[0]  
                
                if nome =="" or nome =="area" or nome == "chans" or nome == "ec_ldd" or nome == "outlets":
                    continue
                dataset = xr.open_dataset(f"{diretorio}/{arquivo}")
                coluna = list(dataset.variables)[-1]
                dataset1 = dataset.copy()
                dataset1[coluna] = dataset[coluna] * fator
                
                os.remove(f"{diretorio}/{arquivo}")
                dataset1.to_netcdf(f"{diretorio}/{arquivo}")
                try:
                    os.remove(f"{self.OUT_DIR}/out/dis.nc")
                except Exception as erro:
                    print("error> " ,erro)
                os.system("lisflood ../settings.xml")
                
                result = pd.read_csv(f"{self.OUT_DIR}/out/chanqWin.tss",skiprows=3)
                lista = []
                indexer = result.columns.values[0]
                for i in result[indexer]:
                    valor = i.split()[1]
                    lista.append(float(valor))
                final[nome] = lista
        
                os.remove(f"{diretorio}/{arquivo}")
                dataset.to_netcdf(f"{diretorio}/{arquivo}")
                final.to_csv(f"./tabelas/resultados/analise_sensibilidade/_{fator}.csv")
                print(final)
        return final
        
    def compara_chuvas(self):
        meu = xr.open_dataset("/discolocal/felipe/lisflood_pm/catch/meteo/chuvas/pr_simepar.nc")
        era5 = xr.open_dataset("/discolocal/felipe/lisflood_pm/catch/meteo/chuvas/pr_era5_corrigido.nc")
        meu_ = meu.pr.resample(time='M').sum('time').to_dataframe()
        era5_ = era5.band_data.resample(time='M').sum('time').to_dataframe()
        
        meu_ = meu_.groupby(level=['time']).mean()
        era5_ = era5_.groupby(level=['time']).mean()
        
        df_merged = pd.DataFrame()
        
        df_merged = pd.merge(era5_,meu_,left_index = True,right_index = True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x = df_merged.index , y = df_merged.band_data,name = "era5",marker_color = "red"))
        fig.add_trace(go.Bar(x= df_merged.index,y=df_merged.pr,name = "simepar", marker_color = "black"))
        fig.write_html("./comparacao_chuvas.html")
        
        
        return df_merged
    
    
    def plota_analise(self,df_place):
        # import plotly.graph_objs as go
        
        df = pd.read_csv(df_place,index_col = 0)
        nome = df_place.split("/")[-1]
        fig = go.Figure()   
        fig.add_trace(go.Scatter(x = df.index , y =  self._obs["horleitura"],name = "obs"))
        
        for coluna in df.columns:

            merged = self._obs
            merged["ls_dis"] = df[coluna].values
            targets = merged["horleitura"]
            predictions = merged["ls_dis"]
            nash_value = (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))
            print(nash_value)
            fig.add_trace(go.Scatter(x = df.index , y = df[coluna],name = f"{coluna} _>{nash_value}"))
        fig.write_html(f"/discolocal/felipe/lisflood_pm/calibracao/tabelas/resultados/analise_sensibilidade/{nome}.html")

    def ativa_era5(self,ativar):
        if ativar == "ERA5":
            pr = xr.open_dataset("/discolocal/felipe/lisflood_pm/catch/meteo/chuvas/pr_era5_corrigido.nc")
            os.remove("/discolocal/felipe/lisflood_pm/catch/meteo/pr.nc")
            pr.to_netcdf("/discolocal/felipe/lisflood_pm/catch/meteo/pr.nc")
            print("Atualmente os dados do ERA5 estão implementados!")
        elif ativar == "simepar":
            pr = xr.open_dataset("/discolocal/felipe/lisflood_pm/catch/meteo/chuvas/pr_simepar.nc")
            os.remove("/discolocal/felipe/lisflood_pm/catch/meteo/pr.nc")
            pr.to_netcdf("/discolocal/felipe/lisflood_pm/catch/meteo/pr.nc")
            print("Atualmente os dados do simepar estão implementados!")
            
    def analisa_diferentes_chuvas(self,df_chuvas):
         '''
         Programa responsavel por rodar diferentes chuvas dentro do lisflood, a fim de analisar quais apresentao maior representatividade da bacia
         Parameters
         ----------
         df_chuvas : Dataframe
             df com dados das chuvas que serão utilizados.

         Returns
         -------
         None.

         '''    
         base = xr.open_dataset("../catch/meteo/pr.nc")
         data = pd.date_range(start="2013-01-03 00:00:00",end = "2023-04-09 00:00:00",freq = "D" )
         df_final = pd.DataFrame(index = data)
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
             
             os.system(f"lisflood {self.SETTINGS_DIR}/settings.xml")
             
             
             self.plota(arquivo_saida = coluna)
             self.df.rename(columns ={"ls_dis":coluna},inplace = True)
             df_final = pd.merge(df_final,self.df,left_index=True,right_index=True,how = "outer")
             df_final.to_csv("/discolocal/felipe/lisflood_pm/calibracao_manual/tabelas/resultados/analise_chuva.csv")
             
             
             
    def analisa_nova_chuva(self,df_chuvas):
        '''
        Programa responsavel por rodar diferentes chuvas dentro do lisflood, a fim de analisar quais apresentao maior representatividade da bacia
        Parameters
        ----------
        df_chuvas : Dataframe
        df com dados das chuvas que serão utilizados.
    
        Returns
        -------
        None.
   
        '''    
        base = xr.open_dataset("../catch/meteo/pr.nc")
        data = pd.date_range(start="2013-01-03 00:00:00",end = "2023-04-09 00:00:00",freq = "D" )
        df_final = pd.DataFrame(index = data)
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
            
            os.system(f"lisflood {self.SETTINGS_DIR}/settings.xml")
            
            
            self.plota(arquivo_saida = coluna)
            self.df.rename(columns ={"ls_dis":coluna},inplace = True)
            df_final = pd.merge(df_final,self.df,left_index=True,right_index=True,how = "outer")
            df_final.to_csv("/discolocal/felipe/lisflood_pm/calibracao_manual/tabelas/resultados/analise_nova_chuva.csv")
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
          
    def ajustar_dimensao_temporal(self,ano):
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
            data_selecionada = dataset.sel(time=slice(f"{ano}-01-01", f"{ano}-12-31"))
            dataset.close()
            
            novo_nome_arquivo = arquivo
            caminho_novo_arquivo = os.path.join(destino, novo_nome_arquivo)
            os.remove(caminho_novo_arquivo)
            data_selecionada.to_netcdf(caminho_novo_arquivo)
            print(f"Arquivo ajustado: {caminho_novo_arquivo}")
            
            
    def compara_multiplos_anos(self,r = 0.2,m = 1000):
        caminho_arquivo = f"{self.SETTINGS_DIR}/compara_anos.xml"  # Substitua pelo caminho correto
        anos = [str(ano) for ano in range(2013, 2024)]  # Ano correspondente
        self.comparando_multiplos_anos = True
        for ano_alvo in anos:
            self.ajustar_parametros_ano(caminho_arquivo, ano_alvo)
            self.ajustar_dimensao_temporal(ano_alvo)
            self.reseta_for_the_best()
            self.executa(ano_alvo,["table2map"],r,m)
            
        self.comparando_multiplos_anos = False
        
    def executar_um_por_ano(self,r = 0.2,m = 1000):
        caminho_arquivo = f"{self.SETTINGS_DIR}/compara_anos.xml"  # Substitua pelo caminho correto
        anos = [str(ano) for ano in range(2013, 2024)]  # Ano correspondente
        self.comparando_multiplos_anos = True
        for ano_alvo in anos:
            self.ajustar_parametros_ano(caminho_arquivo, ano_alvo)
            self.ajustar_dimensao_temporal(ano_alvo)
            self.reseta_for_the_best()
            os.system(f"lisflood {caminho_arquivo}")
            self.ler_saida()
            self.nash_value = self.nash(False)
            self.arquivo_saida = ano_alvo
            self.plota_unico_file()
        self.comparando_multiplos_anos = False
if __name__ == "__main__":
    import xml.etree.ElementTree as ET
    
    caminho_arquivo = "/discolocal/felipe/lisflood_pm/compara_anos.xml"  # Substitua pelo caminho correto
    
    tree = ET.parse(caminho_arquivo)
    root = tree.getroot()
    
    novo_ano = "2017"  # Ano correspondente
    
    for group_element in root.findall(".//group"):
        for textvar_element in group_element.findall('textvar'):
            var_nome = textvar_element.get('name')
            if var_nome == "CalendarDayStart" or var_nome == "timestepInit" or var_nome == "StepStart":
                textvar_element.set('value', novo_ano + "-01-01 00:00")
            elif var_nome == "StepEnd":
                if novo_ano == "2023":
                    textvar_element.set('value', "2023-07-04 00:00")
                else:
                    textvar_element.set('value', novo_ano + "-12-31 00:00")
    
    tree.write(caminho_arquivo)