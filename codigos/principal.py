#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 30 11:57:06 2023

@author: felipe.bortolletto

Arquivo com rotina para ordenar de maneira coerente os dados obtidos!

vemos o padrao a seguir:
                         _lat
y           x                
7046615.942 610148.259 -26.76
            615148.259 -26.76
            620148.259 -26.76
            625148.259 -26.76
            630148.259 -26.76
                      ...
7206615.942 685148.259 -25.32
            690148.259 -25.32
            695148.259 -25.32
            700148.259 -25.32
            705148.259 -25.32
            
Nosso intuito é constituir uma rotina que consiga replicar esse padrão sem perder a estrutura de dados desejada
Atenção! alguns arquivos são salvos diretamente como nc e outros como .tif, teremos que ponderar cada um deles.
"""

import os 
import xarray as xr
import pandas as pd 
 # "../dados/soilgrids/parametros_finais/final": ".tif",
entrada = [
               "../dados/soilhyd",
               "../dados/land_use",
               "../dados/land_use_dependencies/resultado",
               "../dados/channel",
              "../dados/meteo/serie_final/finais",
               "../dados/lai",
              "../dados/maps"
              ]
loc = [".nc",
       ".tif",
       ".tif",
       ".tif",
       ".nc",
        ".tif",
       ".tif"
       ]
saidas = [
    "../catch/maps/soilhyd",
    "../catch/maps/landuse",
    "../catch/table2map",
    "../catch/maps",
    "../catch/meteo",
    "../catch/lai",
    "../catch/maps"
    ]


diretorios = {x: [y,z] for x,z,y in zip( entrada,saidas,loc)}
for diretorio in entrada:
    files = [x for x in os.listdir(diretorio) if x.endswith(diretorios[diretorio][0])]
    print("-------",diretorio,"-------")


    for arquivo in files:
     
        dataset = xr.open_dataset(f"{diretorio}/{arquivo}")
        nome = arquivo.split(".")[0]  
        base_estatica = xr.open_dataset("../dados/base.nc")
        # base_estatica = base_estatica.sortby(dataset.y,ascending=False)
        base_temporal = xr.open_dataset("../dados/base_temporal.nc")

        lista_nomes = list(dataset.variables)
        
        lista_nomes.remove("x")
        lista_nomes.remove("y")
       
        if diretorio == "../dados/lai":
            dataset = dataset.rename({"band":"time"})
        #descobrir o nome da variavel no dataset
        try:
            lista_nomes.remove("spatial_ref")
        except:
            try:
                lista_nomes.remove("transverse_mercator")
            except:
                Geo_text = "Não há geotexto"
        try:
            lista_nomes.remove("band")
        except:
            "parece n ter mais variaveis alem do nome"
        num_lista = len(lista_nomes)
        
        if num_lista == 1:
            espatial = True
            variavel_name = lista_nomes[0]
        elif num_lista == 2:
            espatial = False
            lista_nomes.remove("time")
            variavel_name = lista_nomes[0]
        
        #veremos se o array possui uma dimenção a mais
        try:
            dataset = dataset.sel(band=1)
            dataset = dataset.drop("band")
            dataset = dataset[["y","x",variavel_name]]
        except:
            "n temos a banda : band"
            
            
            # agora iremos ordenar o dataframe da maneira correta
        if (dataset.y.values == base_estatica.y.values).all():
            
            eixoy = "y: Certo!"
        else:
            eixoy = "y: Errado... "
            
            if dataset.y.values[0] == 7206615.942:

                
                dataset = dataset.sortby(dataset.y,ascending=True)
                
                if (dataset.y.values == base_estatica.y.values).all():

                    eixoy = "y: Certo"
                    
                    
        if (dataset.x.values == base_estatica.x.values).all():
            eixox = "x: Certo!"
        else:
            eixoy = "x: Errado... "
        
        # Aqui iremos verificar a ordem das variaveis do dataframe:
        
        lista_vars = list(dataset.variables)
        if lista_vars[-1] != variavel_name:
                lista_vars.remove(variavel_name)
                lista_vars.append(variavel_name)
                dataset = dataset[lista_vars]
        
        
        #agora vamos alterar o nome da variavel para algo mais compreensivel e unico
        dataset = dataset.rename({variavel_name:nome})
        
        lista_vars = list(dataset.variables)
        print(nome,": ")
        print(eixox,eixoy,lista_vars)
        
        dataset.to_netcdf(f"{diretorios[diretorio][1]}/{nome}.nc")
        print()

# teste = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood_metros/dados/lai/laif.tif")
        
# xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood_metros/dados/lai/laif.tif")
#%%
# pastas = ["./maps",
#             "./maps/channel",
#             "./maps/landuse",
#             "./maps/soilhyd",
#             "./table2map",
#             "./lai",
#             "./meteo",
#           ]

# for pasta in pastas:

#     verifica_ncs(pasta,salva = True)
#     print()
#     print(f"################################## {pasta} concluida ^ #########################################")
#     print()
    
#%%

# teste = xr.open_dataset("/discolocal/felipe/LF_pratico/lfmetros/catch/meteo/pr.nc").to_dataframe()


