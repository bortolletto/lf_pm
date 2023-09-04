 
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import xarray as xr




def plota_grafico(df_loc,fator=1,show_obs = True):
    #vazao nova:
    df = pd.read_csv(f'{df_loc}/chanqWin.tss',skiprows=3)
    lista = []
    for i in df["1"]:
        valor = i.split()[1]
        lista.append(float(valor))
    data = pd.date_range(start="2013-01-01 00:00:00",end = "2023-04-30 00:00:00",freq = "D" )
    

    # df2 = pd.read_csv("../catch/out/primeira.tss",skiprows=3)
    # lista2 = []
    # for i in df2["1"]:
    #     valor = i.split()[1]
    #     lista2.append(float(valor)) 
        
    df_resultado = pd.DataFrame(index = data)
    df_resultado["lf_dis"] = lista
    # df_resultado["primeira"] = lista2
    
    df_chuva =pd.read_csv("./tabelas/chuva_no_exutorio.csv",index_col = "time",parse_dates= True)
    df_resultado = pd.merge(df_resultado,df_chuva,left_index = True,right_index = True,how = "outer")
    # df_chuva["versão 0 "] = lista2
    

    obs = pd.read_csv("/discolocal/felipe/aLisflood/vazao_25334953_porto_amazonas_diario.csv",index_col = 0,parse_dates=True)
    
    df_resultado = pd.merge(df_resultado,obs,left_index = True,right_index=True,how = "outer")
    df_resultado = df_resultado["2018":]
    # df_chuva = df_chuva[8:]
    
    fig = go.Figure()
    
    
    fig = make_subplots(specs = [[ { "secondary_y" : True}]])
    
    fig.add_trace(
        go.Bar(x =df_resultado.index ,y = df_resultado["pr"],name = "chuva"),secondary_y = True)
    
    fig.add_trace(
        go.Scatter(x = df_resultado.index,y = df_resultado.lf_dis*fator ,name = f"new vazao LF ",marker_color = "red"),secondary_y = False)
    # fig.add_trace(
    #     go.Scatter(x = df_resultado.index,y = df_resultado.primeira ,name = f"vazao LF"),secondary_y = False)
    # fig.add_trace(
    #     go.Scatter(x = df_resultado.index,y = df_resultado["versão 0 "] ,name = "versão 0"),secondary_y = False)
    
    if show_obs:
        fig.add_trace(
            go.Scatter(x = df_resultado.index,y = df_resultado.horleitura ,name = "vazao observada",marker_color = "black"),secondary_y = False)
    
    fig.update_layout (
        title_text = "Lisflood Comparação no exutorio",
        autosize = True,
        width = 1800
        
        )
    fig["layout"]["yaxis2"]["autorange"] = "reversed"
    fig.write_html(f"{df_loc}/img.html")

plota_grafico("../catch/out",show_obs = True)


  


#%%

# local = "/discolocal/felipe/aLisflood/catch_lisflood/table2map/soildepth3_f.nc"
# df = xr.open_dataset(local).to_dataframe()
# nome = df.columns.values[0]
# df[nome] = 0
# df.to_xarray().to_netcdf("/discolocal/felipe/aLisflood/catch_lisflood/table2map/soildepth3_f.nc")




# local = "/discolocal/felipe/aLisflood/catch_lisflood/parameters/params_LZThreshold.nc"
# df = xr.open_dataset(local).to_dataframe()
# nome = df.columns.values[0]
# df[nome] = 30
# df.to_xarray().to_netcdf("/discolocal/felipe/aLisflood/catch_lisflood/parameters/params_LZThreshold.nc")
