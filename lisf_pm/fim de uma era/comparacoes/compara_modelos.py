 
import pandas as pd 
import xarray as xr 

import plotly.io as pio
import plotly.graph_objs as go
pio.renderers.default = 'browser'

from plotly.subplots import make_subplots

import hydroeval as he
import numpy as np 



gr4 = pd.read_csv("./saida_gr4j_novos_parametros.csv",index_col = 0,parse_dates = True)
gr4.drop(columns = ["vazao","etp"],inplace = True)
gr4.rename(columns = {"horleitura":"chuva"},inplace = True)
sisp = pd.read_csv("./dados_sispishi.csv",index_col = 0,parse_dates = True)
sisp = sisp.resample("D",label = "right",closed = "right").mean()
sisp.index = sisp.index.date
lisflood = pd.read_csv("../tabelas/resultados/validando/esc_base_top.csv",index_col = 0,parse_dates = True)

def nse(predictions, targets):
    return (np.sum((targets-predictions)**2)/np.sum((targets-np.mean(targets))**2))


df = pd.merge(gr4,sisp,left_index=True,right_index=True,how = "outer")
df = pd.merge(df,lisflood,left_index=True,right_index=True,how = "outer")

df = df["2013-02-01":"2019"]
fig = make_subplots(specs = [[ { "secondary_y" : True}]])
fig.add_trace(go.Bar(x = df.index , y = df.chuva,name = "chuva",marker_color = "blue"),secondary_y=True)
fig.add_trace(go.Scatter(x = df.index , y = df.horleitura,name = "OBS",marker_color = "blue"),secondary_y=False)
fig.add_trace(go.Scatter(x = df.index , y = df.Porto_Amazonas,name = "SISP",marker_color = "black"),secondary_y=False)
fig.add_trace(go.Scatter(x = df.index , y = df.Q_fore,name = "GR4J",marker_color = "red"),secondary_y=False)
fig.add_trace(go.Scatter(x = df.index , y = df.ls_sim,name = "LISFLOOD",marker_color = "green"),secondary_y=False)
fig["layout"]["yaxis2"]["autorange"] = "reversed"

integral_obs  = np.trapz(df["horleitura"].fillna(df["horleitura"].mean()))
fig.show()

def cp(df,nome):
    df = df[nome]
    valores_ordenados = df.sort_values().to_frame()
    n = len(valores_ordenados)
    valores_ordenados["p"] = [(n-i+1)/(n+1) for i in range(n)   ]
    valores_ordenados["p-1"] = 1 - valores_ordenados["p"]
    return valores_ordenados


cp_obs = cp(df,"horleitura")
results = pd.DataFrame(index = ["integral_sim","dif_integral","porcentagem","log_nash","kge","r","alpha","beta","nash"])
df.Porto_Amazonas = df.Porto_Amazonas.fillna(327.00325)


fig =  go.Figure()
fig.add_trace(go.Scatter(
    x = cp_obs.horleitura,y = cp_obs.p,name = "obs"
    ))
targets = df["horleitura"]
log_targes = np.log(df["horleitura"]).to_frame()
for i in ["Q_fore","Porto_Amazonas","ls_sim"]:
    cp_sim = cp(df,i)
    fig.add_trace(go.Scatter(
        x = cp_sim[i],y = cp_sim.p,name = i
        )) 
    predictions = df[i]
    log_pred = np.log(predictions).to_frame()
    integral_sim =  np.trapz(df[i].fillna(df[i].mean()))
    
    log_nash = nse(log_pred[i],log_targes["horleitura"])
    kge, r, alpha, beta = he.evaluator(he.kge, predictions, targets)
    nash = nse(predictions,targets)
    dif_integral = integral_sim - integral_obs
    percent = abs(round(100*(dif_integral/integral_obs),2))
    lista = [integral_sim,dif_integral,percent,log_nash,kge,r,alpha,beta,nash]
    results[i] = lista
    
    
fig.show()
    
print(results)


#%%
