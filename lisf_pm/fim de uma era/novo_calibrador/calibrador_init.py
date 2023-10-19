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

from tqdm import tqdm
import plotly.io as pio
import plotly.graph_objs as go
pio.renderers.default = 'browser'

from plotly.subplots import make_subplots
    
import hydroeval as he



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
    
    # sim =  pd.read_csv("../tabelas/resultados/kge0_8.tss",skiprows=3)
    # lista2 = []
    # for i in sim["1"]:
    #     valor = i.split()[1]
    #     lista2.append(float(valor))
    
    
    obs = pd.read_csv("../tabelas/dados/pm_vazao_obs.csv",index_col = 0,parse_dates=True)
    obs = obs["2013-01-01":"2020-12-31"]
    
    obs["ls_sim"] = lista
    # obs["kge8"] = lista2
    return obs

def dds(place_name,Xmin, Xmax,X0, fobj, r=0.2, m=1000):
        # Passo 1
        place = f"../tabelas/resultados/{place_name}.csv"
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
                
                temp = ler_csv_parametros()
                temp = temp.iloc[0:8]
                temp["DefaultValue"]= Xbest
                temp.to_csv(place)
                
                
        # Fim
        return Xbest, Fbest 

    
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
        # nash_value = np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)
        kge, r, alpha, beta = he.evaluator(he.kge, predictions, targets)
        return kge[0]
    
def erro_sem_frac(X):
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
        targets = np.log(dados["horleitura"])
        predictions = np.log(dados["ls_sim"])
        # nash_value = np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2)
        kge, r, alpha, beta = he.evaluator(he.kge, predictions, targets)
        # nash_value = nse(predictions,targets)
        return kge[0]
        # if nash_value > 1 :
        #     return (1 - (-nash_value))
        # else:
        #     return (1 - nash_value)
        

def ativa_parametros(csv):
    # csv = "test_doubleif"
    df_loc = f"../tabelas/resultados/{csv}.csv"
    
    df = pd.read_csv(df_loc,index_col = 0)
    print(df)
    settings_file= "../settings.xml"
    temp_xml = df.loc[df.tipo == "xml"]
    temp_frac = df.loc[df.tipo == "landuse"]
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
    print("novo parametros implementados")
    return df



def cp(df,nome):
    df = df[nome]
    valores_ordenados = df.sort_values().to_frame()
    n = len(valores_ordenados)
    valores_ordenados["p"] = [(n-i+1)/(n+1) for i in range(n)   ]
    valores_ordenados["p-1"] = 1 - valores_ordenados["p"]
    return valores_ordenados


def altera_um(nome,novo_valor,arquivo_xml = "../settings.xml"):
    # df = pd.read_csv("../tabelas/resultados/calibrar.csv",index_col = 0)
    
    # print(df[["ParameterName","DefaultValue"]])
    editar_valor_variavel(arquivo_xml,2,nome,novo_valor)

def nse(predictions, targets):
    return (np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2))


def validando(nome):
    df = ler_saida()
    
    log_nash = nse(np.log(df["ls_sim"]),np.log(df["horleitura"]))
    nash = nse(df["ls_sim"],df["horleitura"])
    # df = df.fillna(df.mean())
    kge, r, alpha, beta = he.evaluator(he.kge, df["ls_sim"], df["horleitura"])

    integral_A = np.trapz(df["ls_sim"].fillna(df.ls_sim.mean()))

    # Calcule a integral de B usando a Regra do Trapézio
    integral_B = np.trapz(df["horleitura"].fillna(df["horleitura"].mean()))

    # Calcule a diferença entre as integrais
    diferenca = integral_B - integral_A
    
    cp_sim = cp(df,"ls_sim")
    cp_obs = cp(df,"horleitura")
    # cp_0 = cp(df,"kge8")
    fig =  go.Figure()
    
    fig.add_trace(go.Scatter(
        x = cp_sim.ls_sim,y = cp_sim.p,name = "simulado"
        ))
    # fig.add_trace(go.Scatter(
    #     x = cp_0["kge8"],y = cp_0.p,name = "original"
    #     ))
    fig.add_trace(go.Scatter(
        x = cp_obs.horleitura,y = cp_obs.p,name = "obs"
        ))
    fig.update_layout(title = "periodo de 2022")
    fig.show()

    chuva = xr.open_dataset("../catch/meteo/pr.nc").to_dataframe()
    chuva =chuva.groupby("time").mean()
    chuva = chuva["2013":"2020"]
    fig = make_subplots(specs = [[ { "secondary_y" : True}]])
    predictions = df.ls_sim
    targets = df.horleitura
    nash = nse(predictions,targets)
    fig.add_trace(go.Bar(x = chuva.index , y = chuva.pr,name = "chuva",marker_color = "blue"),secondary_y=True)
    fig.add_trace(go.Scatter(x = df.index , y = df.ls_sim,name = f"simulado nash: {round(nash,2)}",marker_color = "red"),secondary_y=False)
    # fig.add_trace(go.Scatter(x = df.index , y = df["kge8"],name = f"original: {round(nse(df['kge8'],df['horleitura']),2)}",marker_color = "green"),secondary_y=False)
    fig.add_trace(go.Scatter(x= df.index,y=df.horleitura,name = "obs", marker_color = "black"),secondary_y=False)
    fig.update_layout(title = "periodo de 2013-2020")
    fig["layout"]["yaxis2"]["autorange"] = "reversed"
    fig.show()
    # Imprima os resultados
    print("nash:",round(nash,2))
    print("log_nash",round(log_nash,2))
    print("kge,r,alpha,beta:",kge,r,alpha,beta)
    print("Integral de A:", integral_A)
    print("Integral de B:", integral_B)
    print("Diferença entre as integrais:", round(diferenca,2), "em porcentagem:", abs(diferenca/integral_B))
    
    print()
    print("--------------#---------------")
    print()
    print(cp_sim.describe())
    print()
    print(cp_obs.describe())
    df.to_csv(f"../tabelas/resultados/validando/{nome}_{nash}.csv") 



def calibra_seco():
    ini_calibracao = "2013-01-01"
    final_calibracao = "2015-12-31"
    
    ini_valid = "2022-01-01"
    fim_valid = "2022-12-31"
    
    reseta()
    ajustar_parametros_ano("../settings.xml",ini_calibracao,final_calibracao )
    df = ativa_parametros("calibrar")
    df = df.iloc[0:8]
    X,F = dds("calibrando_seco",df.MinValue,df.MaxValue,df.DefaultValue,erro_sem_frac,r = 0.1,m =300)
    
    df = ativa_parametros("calibrando_seco")
    ajustar_parametros_ano("../settings.xml",ini_valid,fim_valid )
    os.system("lisflood ../settings.xml")
    print("calibracao_feita e rodada, agora so ver os resultados filhao!")

    return X,F

def calibra_umido():
    ini_calibracao = "2015-01-01"
    final_calibracao = "2021-12-31"
    
    ini_valid = "2021-01-01"
    fim_valid = "2021-12-31"
    
    reseta()
    ajustar_parametros_ano("../settings.xml",ini_calibracao,final_calibracao )
    df = ativa_parametros("calibrar")
    df = df.iloc[0:8]
    X,F = dds("calibrando_umido",df.MinValue,df.MaxValue,df.DefaultValue,erro_sem_frac,r = 0.1,m =300)
    
    df = ativa_parametros("calibrando_umido")
    ajustar_parametros_ano("../settings.xml",ini_valid,fim_valid )
    os.system("lisflood ../settings.xml")
    print("calibracao_feita e rodada, agora so ver os resultados filhao!")

    return X,F
def ver_fracs():
    files = [x for x in os.listdir("../catch/maps/landuse") if x.endswith(".nc")]
    for i in files:
        ver = xr.open_dataset("f../catch/maps/landuse/{i}")
        print(ver.to_dataframe())
# def calibra_um_de_cada_vez():
   
#    df = ativa_parametros("calibrar_tudo") 
   
#    for i in df.index:
#        temp = df.loc[i].to_frame().T
#        X,F = dds("calibrar_tudo",temp.MinValue,temp.MaxValue,temp.DefaultValue,erro,r = 0.15 , m =10)
       
if __name__ == "__main__":
    
    # temp = pd.read_csv("../tabelas/resultados/calibrar.csv",index_col = 0)
    # temp = temp[0:8]
    # print(temp[["ParameterName","DefaultValue"]])
    # calibra_seco()
    # reseta()
    # ajustar_parametros_ano("../settings.xml","2021-01-01","2023-07-04" )
    # ativa_parametros("log_nash")
    # altera_um("GwPercValue",3)
    #%%
    validando("primeiro teste")
    
    # ajustar_parametros_ano("../settings.xml","2013-01-01","2020-12-31" )
    # df = pd.read_csv("../tabelas/fator_param_ranges.csv",index_col = 0)
    # # df = df.iloc[0:8]
    # X,F = dds("KGE",df.MinValue,df.MaxValue,df.DefaultValue,erro_sem_frac,r = 0.15 , m =4000)


    # arquivo_xml = "../settings.xml"
    # nome ="Thetar3"
    # novo_valor = 0.179
    # editar_valor_variavel(arquivo_xml,2,nome,novo_valor)
