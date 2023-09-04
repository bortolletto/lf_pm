#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 09:35:20 2023

@author: felipe.bortolletto
"""

'''
primeiramente baixamos os dados, certifique de ter criado os diretorios de destino.
'''
import wget
import numpy as np
import os
from osgeo import gdal


def barra_progresso(current, total, width=80):
    porcentagem = current / total * 100
    print(f'Download: {current} de {total} bytes ({porcentagem:.2f}%)', end='\r')




url = "https://files.isric.org/soilgrids/latest/data"

tipos = ["clay",
          "silt",
          "soc",
          "bdod",
          "phh2o",
          "cec"
         ]
perfil = [
"_0-5cm_mean",
"_100-200cm_mean",
"_15-30cm_mean",
"_30-60cm_mean",
"_5-15cm_mean",
"_60-100cm_mean"
    ]

local_25_32 = [
    "tileSG-025-032/tileSG-025-032_3-1.tif",
    "tileSG-025-032/tileSG-025-032_2-1.tif"
    ]
local_25_31 =[
    "tileSG-025-031/tileSG-025-031_2-4.tif",
    "tileSG-025-031/tileSG-025-031_3-4.tif"
    ]

for atributo in tipos:
    
    for layer in perfil:
        for porta1 in local_25_31:
            if atributo == "bdod" or atributo =="phh2o":
                if porta1 == "tileSG-025-031/tileSG-025-031_2-4.tif":
                    porta1 =     "tileSG-025-031/tileSG-025-031_2-3.tif"
                else:
                    porta1 =     "tileSG-025-031/tileSG-025-031_3-3.tif"

            link = f"{url}/{atributo}/{atributo}{layer}/{porta1}"
            # print(f"{atributo}/{atributo}{layer}/{porta1}")
            wget.download(link, bar=barra_progresso,out = f"../dados/soilgrids/brutos/{atributo}/{layer}/{porta1.split('/')[1]}")
        for porta2 in local_25_32:
            link = f"{url}/{atributo}/{atributo}{layer}/{porta2}"
            # print(f"{atributo}/{atributo}{layer}/{porta2}")
            wget.download(link, bar=barra_progresso,out = f"../dados/soilgrids/brutos/{atributo}/{layer}/{porta2.split('/')[1]}")
    print(f"{atributo} concluido ###########################################################")
    
#%%
'''
Juntar arquivos baixados, posteriormente adicionar isso ao codigo a cima 
'''
import wget
import numpy as np
import os
from osgeo import gdal

tipos = ["clay",
          "silt",
          "soc",
          "bdod",
          "phh2o",
          "cec"
         ]
perfil = [
"_0-5cm_mean",
"_100-200cm_mean",
"_15-30cm_mean",
"_30-60cm_mean",
"_5-15cm_mean",
"_60-100cm_mean"
    ]

for atributo in tipos:
    for layer in perfil:
       files_dir =  f"../dados/soilgrids/brutos/{atributo}/{layer}"
       files = [f for f in os.listdir(files_dir) if f.endswith(".tif")]
       files_completos =[f"{files_dir}/{x}" for x in files]
       gdal.BuildVRT(f"{files_dir}/merged{layer}.tif", files_completos)


'''
reprojeta os mapas gerados:
'''
CRS_FINAL = 'EPSG:31982'
CRS_INICIAL = 'EPSG:54030'
for atributo in tipos:
    print(atributo)
    for layer in perfil:
       files =  f"../dados/soilgrids/brutos/{atributo}/{layer}/merged{layer}.tif"
       saida = f"../dados/soilgrids/brutos/{atributo}/reprojetado/reproj{layer}.tif"
       gdal.Warp(saida, files, dstSRS=CRS_FINAL)
       print(layer)
    
'''
Agora iremos realizar os calculos sobre os dados obtidos, para isso é necessarioadaptar as unidades para as convencionais
dividindo os dados pelo fator de conversão
'''

dct = {
       #variavel : fator
       "bdod":100,
       "cec":10,
       "clay":10,
       "phh2o":10,
       "soc":10,
       "ocd":10,
       "silt":10
       }
for atributo in tipos:
    fator = dct[atributo]
    files_dir =  f"../dados/soilgrids/brutos/{atributo}/reprojetado/"
    files = [f for f in os.listdir(files_dir) if f.endswith(".tif")]
    print(f" Agora teremos os valores propios do atributo {atributo} ")
    print("")
    for i in files:
        # Abrir o raster de entrada
        raster_path = f'{files_dir}{i}'
        raster_dataset = gdal.Open(raster_path)
        
        # Obter a banda de entrada
        
        band = raster_dataset.GetRasterBand(1)

        
        # Executar o cálculo 
        raster_data = band.ReadAsArray()
        resultado = raster_data /fator
        
        
        # Procurar pixels com valor de "no_data" na matriz raster_data
        no_data_value = band.GetNoDataValue()
        pixels_no_data = np.where(raster_data == no_data_value)
        resultado[pixels_no_data] = no_data_value
        resultado = resultado.astype(np.float64)
        
        # Criar um novo arquivo de saída para o raster resultante
        nome = i.split("_")[1]
        saida_path = f"../dados/soilgrids/brutos/{atributo}/resultado/redimensionado_{nome}.tif"
        
        # Definir as informações de projeção e transformação para o arquivo de saída
        driver = gdal.GetDriverByName('GTiff')
        saida_dataset = driver.Create(saida_path, raster_dataset.RasterXSize, raster_dataset.RasterYSize, 1, gdal.GDT_Float64)
        
        saida_dataset.SetProjection(raster_dataset.GetProjection())
        saida_dataset.SetGeoTransform(raster_dataset.GetGeoTransform())
        # Escrever os dados do raster resultante no arquivo de saída
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band.SetNoDataValue(no_data_value)
        
        saida_band.WriteArray(resultado.astype(np.float32))
        
        # Fechar os datasets
        raster_dataset = None
        saida_dataset = None
    
"""        
agora podemos realizer os calculos efetivamente
"""

perfil = [
"_0-5cm",
"_100-200cm",
"_15-30cm",
"_30-60cm",
"_5-15cm",
"_60-100cm"
    ]

def sand(saida,layer):
        
        clay = gdal.Open(f'../dados/soilgrids/brutos/clay/resultado/reprojetado/recortado{layer}.tif')
        silt = gdal.Open(f'../dados/soilgrids/brutos/silt/resultado/reprojetado/recortado{layer}.tif')
        
        c = clay.GetRasterBand(1).ReadAsArray()
        s = silt.GetRasterBand(1).ReadAsArray()

        resultado = 100 - s - c

        
        c_no_data = clay.GetRasterBand(1).GetNoDataValue()
        s_no_data = silt.GetRasterBand(1).GetNoDataValue()
    
        pixels_no_data = np.where(c == c_no_data)
        resultado[pixels_no_data] = c_no_data
        
        pixels_no_data = np.where(s == s_no_data)
        resultado[pixels_no_data] = c_no_data
        
        saida_path = saida
        
        driver = gdal.GetDriverByName('GTiff')
        saida_dataset = driver.Create(saida_path, clay.RasterXSize, clay.RasterYSize, 1, gdal.GDT_Float64)
        saida_dataset.SetProjection(clay.GetProjection())
        saida_dataset.SetGeoTransform(clay.GetGeoTransform())
        
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band.SetNoDataValue(c_no_data)
        
        saida_band.WriteArray(resultado.astype(np.float32))
        
        # Fechar os datasets
        clay = None
        saida_dataset = None
        
        return "Sand calculada!"
    
def thetar(saida,layer):
        
        sand = gdal.Open(f"../dados/soilgrids/parametros_finais/sand_{layer}.tif")
       
        s1 =  sand.GetRasterBand(1)
        s =   s1.ReadAsArray()
        # Definir a condição para aplicar o cálculo
        condicao = (s > 2)  # se o valor do pixel for maior que 2 alterara o valor de sand
      
        no_data_value =  s1.GetNoDataValue()
        pixels_no_data = np.where(s == no_data_value)
        
        # Aplicar o cálculo usando a condição if-else
        resultado = np.where(condicao,0.179 , 0.041)  # (condição,solucao if true, solução if false)
        resultado[pixels_no_data] = no_data_value
       
        saida_path = saida
        
        
        driver = gdal.GetDriverByName('GTiff')
        saida_dataset = driver.Create(saida_path, sand.RasterXSize, sand.RasterYSize, 1, gdal.GDT_Float64)
        saida_dataset.SetProjection(sand.GetProjection())
        saida_dataset.SetGeoTransform(sand.GetGeoTransform())
        
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band = saida_dataset.GetRasterBand(1)
        saida_band.SetNoDataValue(no_data_value)
        
        saida_band.WriteArray(resultado.astype(np.float32))
        s = None
        saida_dataset = None
        
        return "thetar r calculado!"
    

    
def lambda_parameter(saida,layer):
    #leitura dos dados:
    band_clay = gdal.Open(f'../dados/soilgrids/brutos/clay/resultado/reprojetado/recortado{layer}.tif')
    band_silt = gdal.Open(f'../dados/soilgrids/brutos/silt/resultado/reprojetado/recortado{layer}.tif')
    band_bd = gdal.Open(f'../dados/soilgrids/brutos/bdod/resultado/reprojetado/recortado{layer}.tif')
    band_soc = gdal.Open(f'../dados/soilgrids/brutos/soc/resultado/reprojetado/recortado{layer}.tif')


    clay = band_clay.GetRasterBand(1)
    silt = band_silt.GetRasterBand(1)
    bulk = band_bd.GetRasterBand(1)
    org = band_soc.GetRasterBand(1)
    

    
    c = clay.ReadAsArray()
    s = silt.ReadAsArray()
    bd = bulk.ReadAsArray() 
    oc = org.ReadAsArray()
    
    
    c_no_data = clay.GetNoDataValue()
    s_no_data = silt.GetNoDataValue()
    bd_no_data = bulk.GetNoDataValue()
    oc_no_data = org.GetNoDataValue()
    
    if layer == "_0-5cm":
        T = 1
    else: 
        T=0


    resultado = 10**(0.22236-0.30189*bd-0.05558*T-0.005306*c-0.003084*s-0.01072*oc)
    
    pixels_no_data = np.where(c == c_no_data)
    resultado[pixels_no_data] = c_no_data
    
    pixels_no_data = np.where(s == s_no_data)
    resultado[pixels_no_data] = c_no_data
    
    pixels_no_data = np.where(bd == bd_no_data)
    resultado[pixels_no_data] = c_no_data
    
    pixels_no_data = np.where(oc == oc_no_data)
    resultado[pixels_no_data] = c_no_data
    
    saida_path = saida
    driver = gdal.GetDriverByName('GTiff')
    saida_dataset = driver.Create(saida, band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
    saida_dataset.SetProjection(band_clay.GetProjection())
    saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())
    
    saida_band = saida_dataset.GetRasterBand(1)
    saida_band = saida_dataset.GetRasterBand(1)
    saida_band.SetNoDataValue(c_no_data)
    
    saida_band.WriteArray(resultado.astype(np.float32))
    s = None
    saida_dataset = None
        
    return "thetar r calculado!"
def ler_variaveis(var,layer,error = False):
    '''
    le as variaeis necessarias, pode retornar o valor de dados nulos padrao no raster quando erro = True
    '''
    band_clay = gdal.Open(f'../dados/soilgrids/brutos/{var}/resultado/reprojetado/recortado{layer}.tif')
    
    clay = band_clay.GetRasterBand(1)
    
    c = clay.ReadAsArray()
    
    error_value = clay.GetNoDataValue()
    if error  == True:
        return error_value
    else:
        return c
 


def seta_nulos(resultado,c_no_data,padrao):
    '''
    atribui valor de dados nulos ao resultado calculado. 
    
    '''
    pixels_no_data = np.where(resultado == c_no_data)
    resultado[pixels_no_data] = padrao
    return resultado

 
def thetas(saida,layer):
    #leitura
    band_clay = gdal.Open(f'../dados/soilgrids/brutos/clay/resultado/reprojetado/recortado{layer}.tif')
    c = ler_variaveis("clay",layer)
    bd = ler_variaveis("bdod",layer) 
    s = ler_variaveis("silt",layer)

    #contas
    resultado=(0.83080-0.28217*bd+0.0002728*c+0.000187*s)

        
    resultado = np.where(resultado >=100,ler_variaveis("clay",layer,error = True),resultado)
    resultado = np.where((resultado <= -14) & (resultado >= -15),ler_variaveis("clay",layer,error = True),resultado)
    #no_data
    resultado = seta_nulos(resultado,ler_variaveis("clay",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("bdod",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("silt",layer,error = True),ler_variaveis("clay",layer,error = True))
  
    #saida

    saida_path = saida
    driver = gdal.GetDriverByName('GTiff')
    saida_dataset = driver.Create(saida, band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
    saida_dataset.SetProjection(band_clay.GetProjection())
    saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())
    
    saida_band = saida_dataset.GetRasterBand(1)
    saida_band = saida_dataset.GetRasterBand(1)
    saida_band.SetNoDataValue(ler_variaveis("clay",layer,error = True))
    
    saida_band.WriteArray(resultado.astype(np.float32))
    saida_dataset = None
        
    return "thetar s calculado!"

def genu_alpha(saida,layer):
    band_clay = gdal.Open(f'../dados/soilgrids/brutos/clay/resultado/reprojetado/recortado{layer}.tif')
    c = ler_variaveis("clay",layer)
    bd = ler_variaveis("bdod",layer) 
    s = ler_variaveis("silt",layer)
    oc = ler_variaveis("soc",layer)
    
    if layer == "_0-5cm":
        T = 1
    else: 
        T=0
        
    #contas
    
    resultado=10**(-0.43348-0.41729*bd-0.04762*oc+0.21810*T-0.01581*c-0.01207*s)

        
    resultado = np.where(resultado == np.max(resultado),ler_variaveis("clay",layer,error = True),resultado)
       
        
    resultado = seta_nulos(resultado,ler_variaveis("clay",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("bdod",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("silt",layer,error = True),ler_variaveis("clay",layer,error = True))
  
    #saida
    saida_path = saida
    driver = gdal.GetDriverByName('GTiff')
    saida_dataset = driver.Create(saida, band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
    saida_dataset.SetProjection(band_clay.GetProjection())
    saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())
    
    saida_band = saida_dataset.GetRasterBand(1)
    saida_band = saida_dataset.GetRasterBand(1)
    saida_band.SetNoDataValue(ler_variaveis("clay",layer,error = True))
    
    saida_band.WriteArray(resultado.astype(np.float32))
    saida_dataset = None
    return "genu_alpha calculado!"

def k_saturado(saida,layer):
    band_clay = gdal.Open(f'../dados/soilgrids/brutos/clay/resultado/reprojetado/recortado{layer}.tif')
    c = ler_variaveis("clay",layer)
    bd = ler_variaveis("bdod",layer) 
    s = ler_variaveis("silt",layer)
    oc = ler_variaveis("soc",layer)
    ph = ler_variaveis("phh2o",layer)
    cec = ler_variaveis("cec",layer)
    if layer == "_0-5cm":
        T = 1
    else: 
        T=0
        
    #contas
    
    resultado=10**(0.40220+0.26122*ph+0.44565*T-0.02329*c-0.01265*s-0.01038*cec)


    resultado = np.where(resultado == np.min(resultado),ler_variaveis("clay",layer,error = True),resultado)
    resultado = np.where(resultado == np.max(resultado),ler_variaveis("clay",layer,error = True),resultado)
    
   

    resultado = seta_nulos(resultado,ler_variaveis("clay",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("bdod",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("silt",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("soc",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("phh2o",layer,error = True),ler_variaveis("clay",layer,error = True))
    resultado = seta_nulos(resultado,ler_variaveis("cec",layer,error = True),ler_variaveis("clay",layer,error = True))
    
    #saida
    
    saida_path = saida
    driver = gdal.GetDriverByName('GTiff')
    saida_dataset = driver.Create(saida, band_clay.RasterXSize, band_clay.RasterYSize, 1, gdal.GDT_Float64)
    saida_dataset.SetProjection(band_clay.GetProjection())
    saida_dataset.SetGeoTransform(band_clay.GetGeoTransform())
    
    saida_band = saida_dataset.GetRasterBand(1)
    saida_band = saida_dataset.GetRasterBand(1)
    saida_band.SetNoDataValue(ler_variaveis("clay",layer,error = True))
    
    saida_band.WriteArray(resultado.astype(np.float32))
    saida_dataset = None
    return "genu_alpha calculado!"



'''
recorta extenção codigo para recortar raster, executou com erro devido a um pixel invalido!
rever aplicação para bdod


'''

def recorta_arquivos():
    '''
    recorta arquivos mediante certa resolução
    
    '''
    for atributo in tipos:
        # fator = dct[atributo]
        files_dir =  f"../dados/soilgrids/brutos/{atributo}/resultado/"
        files = [f for f in os.listdir(files_dir) if f.endswith(".tif")]
        for i in files:
            nome = i.split("_")[1]
            recortar_raster_por_extensao(f"{files_dir}{i}", "../base.tif", f"{files_dir}reprojetado/recortado_{nome}")
    return "arquivos recortados"

def recortar_raster_por_extensao(arquivo, raster_referencia, arquivo_saida):
    # Abrir o raster de entrada
    raster_dataset = gdal.Open(arquivo)

    # Abrir o raster de referência para obter a extensão
    referencia_dataset = gdal.Open(raster_referencia)
    referencia_geotransform = referencia_dataset.GetGeoTransform()

    # Obter a extensão espacial do raster de referência
    extensao_recorte = (referencia_geotransform[0], referencia_geotransform[3], referencia_geotransform[0] + referencia_dataset.RasterXSize * referencia_geotransform[1], referencia_geotransform[3] + referencia_dataset.RasterYSize * referencia_geotransform[5])

    # Obter as informações de geotransformação do raster de entrada
    geotransform = raster_dataset.GetGeoTransform()

    # Obter a resolução do raster de entrada
    resolucao_x = geotransform[1]
    resolucao_y = geotransform[5]

    # Calcular o tamanho do raster recortado com base na extensão de recorte e na resolução
    tamanho_x = int((extensao_recorte[2] - extensao_recorte[0]) / resolucao_x)
    tamanho_y = int((extensao_recorte[3] - extensao_recorte[1]) / resolucao_y)

    # Configurar as opções de recorte
    opcoes_recorte = ['-projwin', str(extensao_recorte[0]), str(extensao_recorte[1]), str(extensao_recorte[2]), str(extensao_recorte[3])]

    # Realizar o recorte usando a função Translate()
    gdal.Translate(arquivo_saida, raster_dataset, options=opcoes_recorte, width=tamanho_x, height=tamanho_y)

    # Fechar os datasets
    raster_dataset = None
    referencia_dataset = None
    return "reprojetado"





#./bdod/resultado/reprojetado/recortado_30-60cm.tif
def inserir_dados_raster(dados,base, arquivo_saida):
    # Abrir o raster base
    base_dataset = gdal.Open(base)
    base_banda = base_dataset.GetRasterBand(1)
    base_geotransform = base_dataset.GetGeoTransform()

    # Abrir o raster de dados
    dados_dataset = gdal.Open(dados)
    dados_banda = dados_dataset.GetRasterBand(1)

    # Ler os dados do raster base e do raster de dados como matrizes numpy
    base_data = base_banda.ReadAsArray()
    dados_data = dados_banda.ReadAsArray()

    # Verificar se o raster de dados tem uma linha a menos que o raster base
    if base_data.shape[0] - dados_data.shape[0] == 1:
        # Adicionar uma linha de valores nulos ao raster de dados
        linha_nula = np.zeros((1, dados_data.shape[1]), dtype=dados_data.dtype)
        dados_data = np.concatenate((dados_data, linha_nula), axis=0)
    if base_data.shape[1] - dados_data.shape[1] == 1:
        # Adicionar uma coluna de valores nulos ao raster de dados
        coluna_nula = np.zeros((dados_data.shape[0], 1), dtype=dados_data.dtype)
        dados_data = np.concatenate((dados_data, coluna_nula), axis=1)
        
    if base_data.shape[0] - dados_data.shape[0] == -1:
    # Remover a última linha do raster de dados
        dados_data = dados_data[:-1, :]

    if base_data.shape[1] - dados_data.shape[1] == -1:
    # Remover a última coluna do raster de dados
        dados_data = dados_data[:, :-1]
    c_no_data = dados_banda.GetNoDataValue()
    
    # Obter a máscara dos pixels com valor de no_data
    pixels_no_data = np.where(dados_data == c_no_data)
    
    # Adicionar os valores de no_data ao raster final
    base_data = dados_data
    base_data[pixels_no_data] = c_no_data
    


    # Atualizar os valores no raster base com os valores do raster de dados
    base_data = np.where(base_data == 0, dados_data, base_data)

    # Criar um novo arquivo de saída para o raster atualizado
    driver = gdal.GetDriverByName('GTiff')
    saida_dataset = driver.Create(arquivo_saida, base_dataset.RasterXSize, base_dataset.RasterYSize, 1, base_banda.DataType)
    saida_dataset.SetProjection(base_dataset.GetProjection())
    saida_dataset.SetGeoTransform(base_geotransform)
    saida_banda = saida_dataset.GetRasterBand(1)
    saida_banda.WriteArray(base_data)
    saida_banda.SetNoDataValue(c_no_data)
    # Fechar os datasets
    base_dataset = None
    dados_dataset = None
    saida_dataset = None
    

    
    return "Dados inseridos na base raster com sucesso."


def ajeitabdo():
    files_necessitam_novo_shape = [ f".../dados/soilgrids/brutos/bdod/resultado/reprojetado",
                       f"../dados/soilgrids/brutos/silt/resultado/reprojetado",
                        f"../dados/soilgrids/brutos/cec/resultado/reprojetado",
                       f"../dados/soilgrids/brutos/soc/resultado/reprojetado",
                        f"../dados/soilgrids/brutos/phh2o/resultado/reprojetado",
                        f"../dados/soilgrids/brutos/clay/resultado/reprojetado"]
    
    base = "../base.tif"
    
    
    for files_dir_bdod in files_necessitam_novo_shape:
        files1 = [f for f in os.listdir(files_dir_bdod) if f.endswith(".tif")]
        for i in files1:
            nome = i.split("_")[1]
        
       
            # dados = "./bdod/resultado/reprojetado/recortado_100-200cm.tif"
            dados = f"{files_dir_bdod}/{i}"
            inserir_dados_raster(dados, base, dados)
    return "pronto garoto"




tipos = ["clay",
          "silt",
          "soc",
          "bdod",
          "phh2o",
          "cec"
         ]
    
perfil = [
"_0-5cm",
"_100-200cm",
"_15-30cm",
"_30-60cm",
"_5-15cm",
"_60-100cm"
    ]

    
recorta_arquivos()
ajeitabdo()
for layer in perfil:
    
    sand(f"../dados/soilgrids/parametros_finais/sand_{layer}.tif",layer)
    thetar(f"../dados/soilgrids/parametros_finais/thetar/{layer}.tif",layer)
    lambda_parameter(f"../dados/soilgrids/parametros_finais/lambda/{layer}.tif",layer)
    genu_alpha(f"../dados/soilgrids/parametros_finaisgenu/{layer}.tif",layer)
    k_saturado(f"../dados/soilgrids/parametros_finais/ksat/{layer}.tif",layer)
    thetas(f"../dados/soilgrids/parametros_finais/thetas/{layer}.tif",layer)
    
#%% lixo? rever 

