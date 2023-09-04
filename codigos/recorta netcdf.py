'''
Esse arquivo recorta os valores de area desejados para o sistema dado, essa primeira parte pega arquivos netcdf/tif transforma em tifs recortados pelo gdal
A segunda parte coleta eses mesmos arquivos e trata eles para obterem o seguinte formato:
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
'''

import subprocess

import os 


lista = ["maps",
"table2map",
"meteo",
"lai",
"maps/channel",
"maps/landuse",
"maps/soilhyd"
]


ent = "/discolocal/felipe/LF_pratico/lisflood/lisflood_metros/catch"
sai = "/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch"

for local in lista:
    diretorio = f"{ent}/{local}"
    files = [x for x in os.listdir(diretorio) if x.endswith(".nc")]
    print(files)
    for i in files:
        
        arquivo_entrada = f"{ent}/{local}/{i}"
        saida = f"{sai}/{local}/{i.split('.')[0]}"
        subprocess.run(f"gdal_translate -projwin 607648.25 7209116.0 707648.3125 7149115.0 -of GTiff {arquivo_entrada} {saida}.tif",shell = True)

files = ["/discolocal/felipe/LF_pratico/lfmetros/lisvap/out/e0.nc",
"/discolocal/felipe/LF_pratico/lfmetros/lisvap/out/es.nc",
"/discolocal/felipe/LF_pratico/lfmetros/lisvap/out/et.nc"
]
for i in files:
    arquivo_entrada = i
    nome = i.split("/")[-1].split(".")[0]
    saida = f"/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/meteo/"
    subprocess.run(f"gdal_translate -projwin 607648.25 7209116.0 707648.3125 7149115.0 -of GTiff {arquivo_entrada} {saida}{nome}.tif",shell = True)

#%%

import xarray as xr
from osgeo import gdal
import subprocess
import os 
lista = ["maps",
"table2map",
"meteo",
"lai",
"maps/channel",
"maps/landuse",
"maps/soilhyd"
]
base_estatica = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/dados/base.nc")
base_temporal = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/dados/base_temporal.nc")
for local in lista:
    diretorio = f"/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/{local}"
    files = [x for x in os.listdir(diretorio) if x.endswith(".tif")]

    for arquivo in files:
        dataset = xr.open_dataset(f"{diretorio}/{arquivo}")
        nome = arquivo.split(".")[0]  
        # print(nome)
        if nome == "lzavin":
            nome = "lzavin.nc"
        if nome == "ta":
            dataset = dataset.rename({'t': "ta"})
        lista_nomes = list(dataset.variables)
        lista_nomes.remove("x")
        lista_nomes.remove("y")

        
        # dataset = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/chanbnkf.nc")
        
        if "time" in lista_nomes:
            print("temporal")
            dataset = dataset[["time","y","x","spatial_ref",nome]]
        else:
            try:                
                dataset = dataset[["y","x","transverse_mercator",nome]]
            except:
                dataset = dataset[["y","x","spatial_ref",nome]]
        try:
            dataset = dataset.sel(band=1)
            dataset = dataset.drop("band")
        except:
            None
        dataset = dataset.sortby(dataset.y,ascending = True)
        print(list(dataset.variables))
        dataset.to_netcdf(f"{diretorio}/{nome}.nc")
#%%
# import xarray as xr
# from osgeo import gdal
# import subprocess
# import os 
# import numpy as np 
# lista = ["maps",
# "table2map",
# "meteo",
# "lai",
# "maps/channel",
# "maps/landuse",
# "maps/soilhyd"
# ]


# base_estatica = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/area.tif")
# base_estatica = base_estatica.sel(band=1)
# base_estatica = base_estatica.drop("band")

# base_estatica.to_netcdf("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/meteo/teste.nc")
# base_temporal = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/meteo/pr.nc")
# final = np.datetime64('2023-04-07T00:00:00.000000000')
# inicio = np.datetime64('2013-01-01T00:00:00.000000000')
# # base_temporal = base_temporal.sel(time=slice(inicio,final))


# datas_sequenciais = inicio + np.arange(36) * np.timedelta64(10, 'D')


# base_lai  = base_temporal.sel(time=datas_sequenciais)
# for local in lista:
#     diretorio = f"/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/{local}"
#     files = [x for x in os.listdir(diretorio) if x.endswith(".tif")]

#     for arquivo in files:
#         dataset = xr.open_dataset(f"{diretorio}/{arquivo}")
#         nome = arquivo.split(".")[0]  
#         if nome == "area":
#             test1 = dataset.copy
#             break
       
#         if nome == "lzavin":
#             nome = "lzavin.nc"
#         try:
#             dataset = dataset.rename_vars({'band_data': nome})
#         except:
#             None
       
#         if  nome =="ta"or  nome == "e0" or nome == "es" or nome == "et" :
#             dataset = dataset.rename({'band': "time"})
#         # if nome == "ta":
#         #     dataset = dataset.rename({'t': "ta"})
#         try:
#             dataset = dataset.sel(band=1)
#             dataset = dataset.drop("band")
#         except:
#             None
#         values = dataset[nome].values
       
#         if local == "lai":
#             temp = base_lai.copy()
#             temp["band_data"].values =values
#             temp =    temp.rename_vars({'band_data': nome})
#         elif local == "meteo":
           
#             temp = base_temporal.copy()
#             temp["band_data"].values =values
#             temp =    temp.rename_vars({'band_data': nome})

#             # if nome == "ta":
#             #     break
#         else:
#             temp = base_estatica.copy()
#             temp["area"].values =values
#             temp = temp.rename_vars({'area': nome})   
#         temp = temp.sortby(dataset.y,ascending = True)
#         temp.to_netcdf(f"{diretorio}/{nome}.nc")
        
#         print(list(dataset.variables))
# teste = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/meteo/diversos/t.nc")

#%%
# dataset.to_netcdf("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/outros/teste.nc")
# dataset = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/meteo/pr.nc")
# que = xr.open_dataset('/discolocal/felipe/LF_pratico/lisflood/conscistencia de forncantes_chuva/era5/era_5_padrao_paraLF.nc')

#%%
# import xarray as xr
# from osgeo import gdal
# import subprocess
# import os 
# import numpy as np 
# import rasterio
# import pyproj

# lista = ["maps",
# "table2map",
# "meteo",
# "lai",
# "maps/channel",
# "maps/landuse",
# "maps/soilhyd"
# ]

# #%%definindo as cordenadas

# base = xr.open_dataset("/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/maps/area.tif")
# longitude = base.x.values
# latitude  =  base.y.values

# #%%


# for local in lista:
#     diretorio = f"/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/{local}"
#     files = [x for x in os.listdir(diretorio) if x.endswith(".tif")]

#     for arquivo in files:
#         dataset = xr.open_dataset(f"{diretorio}/{arquivo}")
#         nome = arquivo.split(".")[0] 
#         if nome == "lzavin":
#             nome = "lzavin.nc"
#         print(dataset)
        
#         with rasterio.open(f"{diretorio}/{arquivo}") as src:
#             transform = src.transform
            
#             data = src.read(1)

#             print(data.shape)
#             print(crs)
#             print(transform)
#         data = np.transpose(data)
#         crs =  pyproj.CRS.from_string('EPSG:31982')
#         ds = xr.DataArray(data,dims = ("x","y"),coords={'x': longitude,'y': latitude})
#         ds.attrs["transform"] = transform
#         ds.attrs['crs'] = crs.to_wkt()
#         ds.to_netcdf('/discolocal/felipe/LF_pratico/lisflood/porto_amazonas/catch/out/teste.nc')


# test = xr.open_dataset("/discolocal/felipe/aLisflood/lisflood/lisflood-code/tests/data/LF_ETRS89_UseCase/maps/soilhyd/genua3.nc")
