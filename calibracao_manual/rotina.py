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

class Altera_Xml():
    
    def ler_variaveis_grupo(self,grupo_element):
        grupo = {}
        for textvar_element in grupo_element.findall('textvar'):
            var_nome = textvar_element.get('name')
            var_valor = textvar_element.get('value')
            grupo[var_nome] = var_valor
        return grupo

    # Função para ler todos os grupos e suas variáveis dentro do elemento <lfuser>
    def ler_grupos_lfuser(self,arquivo_xml,ler_variaveis_grupo):
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()

        lfuser_element = root.find('lfuser')

        grupos_variaveis = []
        for group_element in lfuser_element.findall('group'):
            grupo = ler_variaveis_grupo(group_element)
            grupos_variaveis.append(grupo)

        return grupos_variaveis

    def editar_valor_variavel(self,arquivo_xml, grupo_index, variavel, novo_valor):
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()

        lfuser_element = root.find('lfuser')
        grupo_element = lfuser_element.findall('group')[grupo_index]
        
        novo_valor = str(novo_valor)
            
        for textvar_element in grupo_element.findall('textvar'):
            var_nome = textvar_element.get('name')
            if var_nome == variavel:
                textvar_element.set('value', novo_valor)
                break
        tree.write(arquivo_xml)
        
    
    def ajustar_parametros_ano(self,arquivo_xml, novo_ano):
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()
    
        for group_element in root.findall(".//group"):
            for textvar_element in group_element.findall('textvar'):
                var_nome = textvar_element.get('name')
                if var_nome == "CalendarDayStart" or var_nome == "timestepInit" or var_nome == "StepStart":
                    textvar_element.set('value', novo_ano + "-01-01 00:00")
                    self.data_inicial = novo_ano + "-01-01 00:00"
                elif var_nome == "StepEnd":
                    if novo_ano == "2023":
                        textvar_element.set('value', "2023-07-04 00:00")
                        self.data_final = "2023-04-07 00:00"
                    else:
                        textvar_element.set('value', novo_ano + "-12-31 00:00")
                        self.data_final = novo_ano + "-12-31 00:00"

        
        tree.write(arquivo_xml)

        
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

       
    def manipular(self,substituir = True):
        if substituir:
            for arquivo in self.files:

                   self.dataset = xr.open_dataset(f"{self.diretorio_entrada}{arquivo}")
                   self.name_var = list(self.dataset.variables)[-1]     
                   self.dataset[self.name_var].values = [[self._fator for _ in range(len(self.dataset.x))] for _ in range(len(self.dataset.y))]
    
                   os.remove(f"{self.diretorio_saida}{arquivo}")
    
                   self.dataset.to_netcdf(f"{self.diretorio_saida}{arquivo}")

        else:
               for arquivo in self.files:

                   self.dataset = xr.open_dataset(f"{self.diretorio_entrada}{arquivo}")
                   self.name_var = list(self.dataset.variables)[-1]     
                   self.dataset[self.name_var].values = self.dataset[self.name_var].values * self._fator

                   os.remove(f"{self.diretorio_saida}{arquivo}")

                   self.dataset.to_netcdf(f"{self.diretorio_saida}{arquivo}")
 #%% 
 ######################## old dds ###############################
    def dds(self,Xmin, Xmax, fobj,df, r=0.2, m=1000):
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
          # Passo 3
          for i in tqdm(I):
            
              Pi = 1 - np.log(i)/np.log(m)
              P = np.random.rand(len(Xmin))
              N = np.where(P < Pi)[0]
             
              if N.size == 0:
                  N = [np.random.choice(ds)]
              # Passo 4
              Xnew = np.copy(Xbest)
             
              for j in N:
                  Xnew[j] = Xbest[j] + r*dX[j]*np.random.normal(0, 1)
                  if Xnew[j] < Xmin[j]:
                      Xnew[j] = Xmin[j] + (Xmin[j] - Xnew[j])
                      if Xnew[j] > Xmax[j]:
                          Xnew[j] = Xmin[j]
                  elif Xnew[j] > Xmax[j]:
                      Xnew[j] = Xmax[j] - (Xnew[j] - Xmax[j])
                      if Xnew[j] < Xmin[j]:
                          Xnew[j] = Xmax[j]
              # Passo 5
              Fnew = fobj(Xnew)
              if Fnew <= Fbest:
                  Fbest = Fnew
                  Xbest = np.copy(Xnew)
                  print(Fbest)
                  df[Fbest] = Xbest
                 
          # Fim
          return Xbest, Fbest ,df
    
    ######################## old dds ###############################   
    
  #%% 
  
    # def dds(self, Xmin, Xmax, fobj, df, r=0.2, m=1000):
    #    Xmin = np.asarray(Xmin)
    #    Xmax = np.asarray(Xmax)
    #    X0 = (Xmin + Xmax) / 2
    #    D = len(Xmin)
    #    ds = [i for i in range(D)]
    #    dX = Xmax - Xmin
    #    I = np.arange(1, m + 1, 1)
    #    Xbest = X0
    #    Fbest = fobj(Xbest)

    #    for i in tqdm(I):
    #         Pi = 1 - np.log(i) / np.log(m)
    #         P = np.random.rand(len(Xmin))
    #         N = np.where(P < Pi)[0]
    
    #         if N.size == 0:
    #             N = [np.random.choice(ds)]
    
    #         # Passo 4
    #         Xnew = np.copy(Xbest)
    #         current_frac_sum = sum(Xnew[18:24])  # Soma atual dos parâmetros "frac"
    
    #         for j in N:
    #             if j >= 18 and j <= 23:  # Parâmetros "frac"
    #                 delta_frac = r * dX[j] * np.random.normal(0, 1)
    #                 new_frac = Xbest[j] + delta_frac
    
    #                 # Ajustar os parâmetros "frac" para manter a soma em 1
    #                 Xnew[j] = new_frac
    #                 current_frac_sum += delta_frac
    
    #                 for k in range(18, 24):
    #                     if k != j:
    #                         Xnew[k] = Xnew[k] - delta_frac * Xnew[k] / (1 - new_frac)
    
    #                 # Garantir que os valores estejam entre 0 e 1
    #                 Xnew[j] = max(0, min(1, Xnew[j]))
    
    #             else:
    #                 Xnew[j] = Xbest[j] + r * dX[j] * np.random.normal(0, 1)
    
    #                 if Xnew[j] < Xmin[j]:
    #                     Xnew[j] = Xmin[j] + (Xmin[j] - Xnew[j])
    #                     if Xnew[j] > Xmax[j]:
    #                         Xnew[j] = Xmin[j]
    #                 elif Xnew[j] > Xmax[j]:
    #                     Xnew[j] = Xmax[j] - (Xnew[j] - Xmax[j])
    #                     if Xnew[j] < Xmin[j]:
    #                         Xnew[j] = Xmax[j]
    
    #         # Passo 5
    #         Fnew = fobj(Xnew)
    #         if Fnew <= Fbest:
    #             Fbest = Fnew
    #             Xbest = np.copy(Xnew)
    #             print(Fbest)
    #             df[Fbest] = Xbest
    
    #     # Fim
    #    return Xbest, Fbest, df
    #%%
    def nash(self,recorta = False,kge = False):
        if kge == False:
            self.df_merged = pd.merge(self.df,self._obs,left_index= True,right_index= True)
            if recorta == True:
                self.df_merged = self.df_merged["2017":]
            targets = self.df_merged["horleitura"]
            predictions = self.df_merged["ls_dis"]
            self.nome_grafico = "nash"
            return (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))
        
        elif kge == True:
            import hydroeval as he
            self.df_merged = pd.merge(self.df,self._obs,left_index= True,right_index= True)
            targets = self.df_merged["horleitura"]
            predictions = self.df_merged["ls_dis"]
            # nse = he.evaluator(he.nse, simulations, evaluations)
            kge, r, alpha, beta = he.evaluator(he.kge, predictions, targets)
            self.nome_grafico = "KGE"        
            return (1 - kge[0])
        else:
            self.df_merged = pd.merge(self.df,self._obs,left_index= True,right_index= True)
            if recorta == True:
                self.df_merged = self.df_merged["2017":]
            targets = self.df_merged["horleitura"]
            predictions = self.df_merged["ls_dis"]
            
            import hydroeval as he
            self.df_merged = pd.merge(self.df,self._obs,left_index= True,right_index= True)

            # nse = he.evaluator(he.nse, simulations, evaluations)
            kge, r, alpha, beta = he.evaluator(he.kge, predictions, targets)
            nash = (1-(np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)))
            self.nome_grafico = "nash_kge"
            return (kge[0] + nash)
        
    


    def ler_saida(self):
        df_loc = f"{self.OUT_DIR}/out/"
        sim = pd.read_csv(f"{df_loc}/chanqWin.tss",skiprows=3)
        # df_loc = "/discolocal/felipe/lisflood_pm/catch/out/"
        lista = []
        for i in sim["1"]:
            valor = i.split()[1]
            lista.append(float(valor))
        if len(lista) <= 400:
            data = pd.date_range(start=self.data_inicial,end = self.data_final,freq = "D" )
        else:
            data = pd.date_range(start="2013-01-03 00:00:00",end = "2023-04-09 00:00:00",freq = "D" )
        
        self.df = pd.DataFrame(index = data)
        self.df["ls_dis"] = lista
        
        
        

    def plota(self,recorta = False,plt_esp = False,arquivo_saida = False):
        if arquivo_saida != False:
            self.arquivo_saida = arquivo_saida
        # df_loc = f"{self.OUT_DIR}/out/"
        local_pasta = f"{self.FILE_DIR}tabelas/resultados/plt_geral/"
        data_hoje = datetime.date.today()
        if plt_esp == False:
            self.pasta = f"{local_pasta}{data_hoje.day}_{data_hoje.month}/"
        elif plt_esp:
            self.pasta = f"{self.FILE_DIR}/tabelas/resultados/plt_esp/"
        self.ler_saida()
        self.nash_value = self.nash(recorta)
        
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
    def plota_unico_file(self,recorta = False,plt_esp = False,arquivo_saida = False):
        local_pasta = f"{self.FILE_DIR}tabelas/resultados/plt_geral/"
        data_hoje = datetime.date.today()
        if plt_esp == False:
            self.pasta = f"{local_pasta}{data_hoje.day}_{data_hoje.month}/"
        elif plt_esp:
            self.pasta = f"{self.FILE_DIR}/tabelas/resultados/plt_esp/"
        with open(f'{local_pasta}/ano_a_ano.html', 'a') as f:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x = self.df_merged .index , y = self.df_merged .ls_dis,name = f"simulado {self.nome_grafico}: {self.nash_value}",marker_color = "red"))
            fig.add_trace(go.Scatter(x= self.df_merged .index,y=self.df_merged .horleitura,name = "obs", marker_color = "black"))
            fig.update_layout (
                title_text = self.arquivo_saida)
            if not os.path.exists(self.pasta ):
                os.makedirs(self.pasta )
                print(f"Pasta '{self.pasta }' criada com sucesso.")
            else:
                print(f"A pasta '{self.pasta }' já existe.")
    
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        
    def erro(self,X,substituir = True,recorta = False):
        
        self.nomes_paramns["valores"]= X
        print(self.nomes_paramns)
        if self.comparando_multiplos_anos == True:
           settings_file =  f"{self.SETTINGS_DIR}/compara_anos.xml"
        else:
            settings_file = f"{self.SETTINGS_DIR}/settings.xml"
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
                     
        os.system(f"lisflood {settings_file}")

        self.ler_saida()
        self.nash_value = self.nash(recorta)
        return (1 - self.nash_value)
    