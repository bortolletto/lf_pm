import pandas as pd
import os
import plotly.io as io
import plotly.graph_objs as go
import numpy as np
io.renderers.default='browser'


files = os.listdir("./chuva_simepar")
data = pd.date_range("2010-01-01","2023-08-26",freq="1H")
final = pd.DataFrame(index = data)
for est in files:
    nome = est.split("_")[3].split(".")[0]
    df = pd.read_csv(f"./chuva_simepar/{est}",index_col = 0 ,parse_dates = True)
    
    df.rename(columns={"horleitura": nome,
                       
                       },inplace = True)
    df = df.loc[df.horqualidade == 0]
    df.drop(columns = ["horqualidade"],inplace = True)
    
    final = pd.merge(final,df,how = "outer",left_index=True,right_index=True)
final = final.resample("D",closed = "left",label = "right").sum(min_count = 20)
final["media"] = final.mean(axis = 1)
anual = final.resample("Y",closed = "left",label = "right").sum(min_count = 150)
#%%
def plota(df,titulo,x = None,y = None):
    fig = go.Figure()    
    if x == None:
        for columns in df:
            
            fig.add_trace(go.Bar(x = df.index , y = df[columns],name = columns))
            
    else:
            fig.add_trace(go.Scatter(x = x , y = y,name = columns))
    fig.update_layout (
        title_text = titulo,
        autosize = True,
        width = 1800
        )
    fig.show()
    
def plot_curva_permanencia(data, xlabel, ylabel):
    """
    Plota uma curva de permanência usando Plotly.

    Args:
        data (list or numpy array): Uma lista ou array de valores que você deseja plotar na curva de permanência.
        xlabel (str): Rótulo do eixo x.
        ylabel (str): Rótulo do eixo y.
    """

    # Classifique os dados em ordem crescente
    fig = go.Figure()
    for columns in data:
        # sorted_data = np.sort(data[columns])
    
        # # Calcule a distribuição acumulada
        # cumulative_data = np.arange(1, len(sorted_data) + 1) / len(sorted_data) * 100
    
        # Crie o gráfico usando Plotly
        sorted_data = data[columns].sort_values().to_frame()
        n = len(sorted_data)
        sorted_data["p"] = [(n-i+1)/(n+1) for i in range(n)]
        sorted_data["p-1"] = 1 - sorted_data["p"]

        # vazao_desejada = sorted_data.loc[sorted_data["p-1"] <= Q+0.0001]
        # vazao_desejada = vazao_desejada.iloc[-1].vazao
        
        fig.add_trace(go.Scatter(y=sorted_data[columns], x=sorted_data["p"], mode='lines',connectgaps = False,name = columns))
        fig.update_layout(
            title='Curva de Permanência',
            # xaxis_title=xlabel,
            # yaxis_title=ylabel,
        )

    # Exiba o gráfico
    fig.show()

# plota(final,"chuva_diaria")
# plota(anual,"chuva_anual")
plot_curva_permanencia(final,"dados_organizados","acumulada")


#%%vazao

files = os.listdir("./vazao_simepar")
data = pd.date_range("2010-01-01","2023-08-26",freq="1H")
final = pd.DataFrame(index = data)
for est in files:
    nome = est.split("_")[3].split(".")[0]
    df = pd.read_csv(f"./vazao_simepar/{est}",index_col = 0 ,parse_dates = True)

    df.rename(columns={"horleitura": nome,
                       
                       },inplace = True)
    # df = df.loc[df.horqualidade == 0]
    df.drop(columns = ["horqualidade"],inplace = True)
    
    final = pd.merge(final,df,how = "outer",left_index=True,right_index=True)
final = final.resample("D",closed = "left",label = "right").mean()
final["media"] = final.mean(axis = 1)
anual = final.resample("Y",closed = "left",label = "right").mean()

plot_curva_permanencia(final,"dados_organizados","acumulada")
