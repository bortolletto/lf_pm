#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 10:39:13 2023

@author: felipe.bortolletto
"""
import pandas as pd 
import os 
import xarray as xr
import xml.etree.ElementTree as ET
import numpy as np
from tqdm import tqdm
import hydroeval as he

class Calibra_individual():
    def reseta(self,files = None,nominal = None):
        
        if files == None:
            diretorios = [x for x in os.listdir("./params_calibration")]
            lista_arquivos_maps =[f"./maps/{y}" for y in [x for x in os.listdir("./params_calibration/maps/") if not x.endswith(".nc")]]
            diretorios += lista_arquivos_maps
        elif files != None:
            diretorios = [f"./paramns_calibration/{x}" for x in files]
        if nominal == None:
            for pasta in diretorios:
                dir_entrada = f"./params_calibration/{pasta}/"
                arquivos_originais = [x for x in os.listdir(dir_entrada) if x.endswith(".nc")]
                dir_saida   = f"../catch/{pasta}/"
                for dx in arquivos_originais:
                    dataset = xr.open_dataset(f"{dir_entrada}{dx}")
                    os.remove(f"{dir_saida}{dx}")
                    dataset.to_netcdf(f"{dir_saida}{dx}")
                print( f"A pasta {pasta} voltou ao original")
       
        elif nominal != None:
            for pasta in nominal:
                dir_entrada = f"./params_calibration/{pasta}"
                dir_saida   = f"../catch/{pasta}"
                dataset = xr.open_dataset(f"{dir_entrada}")
                os.remove(f"{dir_saida}")
                dataset.to_netcdf(f"{dir_saida}")
                print( f"O arquivo {pasta.split('/')[-1]} voltou ao original")
        
    
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
        name = "lfuser"
        lfuser_element = root.find(name)
        grupo_element = lfuser_element.findall('group')[grupo_index]
        
        novo_valor = str(novo_valor)
    
        for textvar_element in grupo_element.findall('textvar'):
            var_nome = textvar_element.get('name')
            
            if var_nome == variavel:
                textvar_element.set('value', novo_valor)
                break
        tree.write(arquivo_xml)
        
    
    def ajustar_parametros_ano(self,arquivo_xml, novo_ano,final_ano):
        # arquivo_xml = "/discolocal/felipe/git_pm/settings_base.xml"
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()
    
        for group_element in root.findall(".//group"):
            for textvar_element in group_element.findall('textvar'):
       
                var_nome = textvar_element.get('name')
                if var_nome == "CalendarDayStart" or var_nome == "timestepInit" or var_nome == "StepStart":
                    textvar_element.set('value', novo_ano)
                elif var_nome == "StepEnd":
                        textvar_element.set('value', final_ano)
    
    
        tree.write(arquivo_xml)
    def ler_csv_parametros(self):
        nomes_paramns = pd.read_csv("../tabelas/fator_param_ranges.csv",index_col = 0)
        return nomes_paramns
    
    def ler_saida(self):
        sim =  pd.read_csv("../catch/out/chanqWin.tss",skiprows=3)
        lista = []
        for i in sim["1"]:
            valor = i.split()[1]
            lista.append(float(valor))
        
        # sim =  pd.read_csv("../tabelas/resultados/kge0_8.tss",skiprows=3)
        # lista2 = []
        # for i in sim["1"]:
        #     valor = i.split()[1]
        #     lista2.append(float(valor))
        
        
        obs = pd.read_csv("../tabelas/pm_vazao_obs.csv",index_col = 0,parse_dates=True)
        obs = obs["2013-01-01":"2020-12-31"]
        
        obs["ls_sim"] = lista
        # obs["kge8"] = lista2
        return obs
    def dds(self,place_name,Xmin, Xmax,X0, fobj, r=0.2, m=1000):
            # Passo 1
            place = f"../tabelas/resultados/validando/calibrando individual/{place_name}.csv"
            
            Xmin = np.asarray(Xmin)
            Xmax = np.asarray(Xmax)
            # X0 = (Xmin + Xmax)/2
            D = len(Xmin)
            ds = [i for i in range(D)]
            dX = Xmax - Xmin
            # Passo 2
            I = np.arange(1, m+1, 1)
            Xbest = X0.values
            Fbest = fobj(Xbest)
            # Fbest =  abs(1 - fobj(X0))
            # Passo 3
            for i in tqdm(I):
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
                # Passo 5
                Fnew = fobj(Xnew)
                print(Fbest)
                if Fnew < 1 and abs(1 - Fnew) < abs(1 - Fbest):
                    
                    Fbest = Fnew
                    Xbest = np.copy(Xnew)
                    temp = self.ler_csv_parametros()
                    # temp = temp.iloc[0:8]
                    temp["DefaultValue"]= Xbest
                    temp.to_csv(place)
                    
                    
            # Fim
            return Xbest, Fbest         
    def erro_singular(self,X):
        self.parametro["DefaultValue"] 
        
        settings_file= "../settings.xml"
        temp_xml =  self.parametro.loc[ self.parametro.tipo == "xml"]
        temp_frac =  self.parametro.loc[ self.parametro.tipo == "landuse"]
        for variavel,nome  in zip( temp_xml["DefaultValue"],temp_xml["ParameterName"]) : 
                   self.editar_valor_variavel(settings_file,2,nome,variavel)
        for variavel,nome  in zip( temp_frac["DefaultValue"],temp_frac["ParameterName"]) : 
                 diretorio_entrada = f"./params_calibration/maps/landuse/{nome}.nc"
                 dataset = xr.open_dataset(diretorio_entrada)
                 diretorio_saida = f"../catch/maps/landuse/{nome}.nc"
                 
                 name_var = list(dataset.variables)[-1]     
                 dataset[name_var].values = [[variavel for _ in range(len(dataset.x))] for _ in range(len(dataset.y))]
                 os.remove(diretorio_saida)
                 dataset.to_netcdf(diretorio_saida)
                 
        os.system(f"lisflood {settings_file}")
    
        dados = self.ler_saida()
        self.saidas[self.parametro.DefaultValue.values[0]] = dados.ls_sim
        targets = dados["horleitura"]
        predictions = dados["ls_sim"]
        # nash_value = np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)
        kge, r, alpha, beta = he.evaluator(he.kge, predictions, targets)
        return kge[0]
   
  
    def ativa_parametros(self,csv):
        # csv = "test_doubleif"
        df_loc = f"../tabelas/resultados/{csv}.csv"
        
        df = pd.read_csv(df_loc,index_col = 0)
        settings_file= "../settings.xml"
        temp_xml = df.loc[df.tipo == "xml"]
        temp_frac = df.loc[df.tipo == "landuse"]
        for variavel,nome  in zip( temp_xml["DefaultValue"],temp_xml["ParameterName"]) : 
                   self.editar_valor_variavel(settings_file,2,nome,variavel)
        for variavel,nome  in zip( temp_frac["DefaultValue"],temp_frac["ParameterName"]) : 
                 diretorio_entrada = f"./params_calibration/maps/landuse/{nome}.nc"
                 dataset = xr.open_dataset(diretorio_entrada)
                 diretorio_saida = f"../catch/maps/landuse/{nome}.nc"
                 
                 name_var = list(dataset.variables)[-1]     
                 dataset[name_var].values = [[variavel for _ in range(len(dataset.x))] for _ in range(len(dataset.y))]
                 os.remove(diretorio_saida)
                 dataset.to_netcdf(diretorio_saida)
        print("novo parametros implementados")
        return df
    
    def inicializar(self):
        df = self.ativa_parametros("calibrar_tudo") 
        
        for i in df.index:
            self.saidas = pd.DataFrame()    
            temp = df.loc[i].to_frame().T
            print(temp)
            self.parametro = temp.copy()
            nome = self.parametro.ParameterName.values[0]
            
            X,F = self.dds(nome,self.parametro.MinValue,self.parametro.MaxValue,self.parametro.DefaultValue,self.erro_singular,r = 0.5 , m =10)
            
            self.saidas.to_csv(f"../tabelas/resultados/validando/calibrando individual/saidas_{nome}.csv")    
   
if __name__ == "__main__":
    bora = Calibra_individual()
    bora.inicializar()
