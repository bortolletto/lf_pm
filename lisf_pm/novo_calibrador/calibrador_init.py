#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 09:40:46 2023

@author: felipe.bortolletto
"""

import os 
import xarray as xr 
import pandas as pd 
import xml.etree.ElementTree as ET
import numpy as np
import datetime 
from tqdm import tqdm
def reseta(files = None,nominal = None):
    
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
    

def ler_variaveis_grupo(grupo_element):
    grupo = {}
    for textvar_element in grupo_element.findall('textvar'):
        var_nome = textvar_element.get('name')
        var_valor = textvar_element.get('value')
        grupo[var_nome] = var_valor
    return grupo

# Função para ler todos os grupos e suas variáveis dentro do elemento <lfuser>
def ler_grupos_lfuser(arquivo_xml,ler_variaveis_grupo):
    tree = ET.parse(arquivo_xml)
    root = tree.getroot()

    lfuser_element = root.find('lfuser')

    grupos_variaveis = []
    for group_element in lfuser_element.findall('group'):
        grupo = ler_variaveis_grupo(group_element)
        grupos_variaveis.append(grupo)

    return grupos_variaveis

def editar_valor_variavel(arquivo_xml, grupo_index, variavel, novo_valor):
    tree = ET.parse(arquivo_xml)
    root = tree.getroot()
    name = "lfuser"
    lfuser_element = root.find(name)
    grupo_element = lfuser_element.findall('group')[grupo_index]
    
    novo_valor = str(novo_valor)

    for textvar_element in grupo_element.findall('textvar'):
        var_nome = textvar_element.get('name')
        
        if var_nome == variavel:
            print(var_nome,novo_valor)    
            textvar_element.set('value', novo_valor)
            break
    tree.write(arquivo_xml)
    

def ajustar_parametros_ano(arquivo_xml, novo_ano,final_ano):
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
def ler_csv_parametros():
    nomes_paramns = pd.read_csv("../tabelas/fator_param_ranges.csv",index_col = 0)
    return nomes_paramns

def ler_saida():
    sim =  pd.read_csv("../catch/out/chanqWin.tss",skiprows=3)
    lista = []
    for i in sim["1"]:
        valor = i.split()[1]
        lista.append(float(valor))
    obs = pd.read_csv("../tabelas/pm_vazao_obs.csv",index_col = 0,parse_dates=True)
    obs = obs["2013-01-01":"2020-12-31"]
    
    obs["ls_sim"] = lista
    return obs
def dds(self,Xmin, Xmax,X0, fobj, r=0.2, m=1000):
        # Passo 1
        data_hoje = datetime.date.today()
        pasta = f"../tabelas/resultados/{data_hoje.day}_{data_hoje.month}"
        place = f"{pasta}/rodada_atual.csv"
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
            if Fnew <= Fbest:
                Fbest = Fnew
                Xbest = np.copy(Xnew)
                
                if not os.path.exists(place):
                    os.makedirs(pasta)
                    print(f"Pasta '{self.pasta }' criada com sucesso.")
                temp = ler_csv_parametros()
                temp["DefaultValue"]= Xbest
                temp.to_csv(place)
                print(f"Arquivo '{place}' criado com sucesso.")
                
        # Fim
        return Xbest, Fbest 
def erro():
    
    def erro(X):
        nomes_paramns = ler_csv_parametros()
        nomes_paramns["DefaultValue"]= X

        settings_file= "../settings.xml"
        temp_xml = nomes_paramns.loc[nomes_paramns.tipo == "xml"]
        temp_frac = nomes_paramns.loc[nomes_paramns.tipo == "landuse"]
        for variavel,nome  in zip( temp_xml["DefaultValue"],temp_xml["ParameterName"]) : 
                   editar_valor_variavel(settings_file,2,nome,variavel)
        for variavel,nome  in zip( temp_frac["DefaultValue"],temp_frac["ParameterName"]) : 
                 diretorio_entrada = f"./params_calibration/maps/landuse/{nome}.nc"
                 dataset = xr.open_dataset(diretorio_entrada)
                 diretorio_saida = f"../catch/maps/landuse/{nome}.nc"
                 
                 name_var = list(dataset.variables)[-1]     
                 dataset[name_var].values = [[variavel for _ in range(len(dataset.x))] for _ in range(len(dataset.y))]
                 os.remove(diretorio_saida)
                 dataset.to_netcdf(diretorio_saida)
                 
        os.system(f"lisflood {settings_file}")

        dados = ler_saida()
        targets = dados["horleitura"]
        predictions = dados["ls_sim"]
        nash_value = np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)
        
        # return nash_value
        if nash_value > 1 :
            return (1 - (-nash_value))
        else:
            return (1 - nash_value)
        
    return 

if __name__ == "__main__":
    reseta()
    ajustar_parametros_ano("../settings.xml","2013-01-01","2020-12-31" )
    # arquivo_xml = "../settings.xml"
    # nome ="Thetar3"
    # novo_valor = 0.179
    # editar_valor_variavel(arquivo_xml,2,nome,novo_valor)
