"""
Created on Fri Aug 11 13:35:04 2023

@author: felipe.bortolletto
Criar app para visualizacao

"""



import pandas as pd 
from dash import dcc ,html , Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
from dash import dash_table
from init import Calibrador

class App(Calibrador):
    def leituras(self):
        self.inicializar()
        self.variaveis = pd.read_csv("./tabelas_app/variaveis.csv")
        print(self.variaveis )

        dct = {}
        for i,z in zip (self.variaveis.classe.unique(),self.variaveis.descrição):
            dct[i] = [x for x in self.variaveis.loc[self.variaveis.classe == i,"descrição"]]
            
        self.dloc = pd.read_csv("./tabelas_app/estacoes.csv",index_col =0)
        
        self.meteo= pd.read_csv("./tabelas_app/df_m.csv",index_col = ["time","x","y"],parse_dates = True)
        # dados_meteo.rename(columns = {"media_test_y": "sum_dados"},inplace =True)

        # estaticos = pd.read_csv("/discolocal/felipe/aLisflood/lisf_apresnt/app/dados_estaticos_gerais.csv",index_col = ["y","x"])
        self.estaticos=pd.read_csv("./tabelas_app/df_e.csv",index_col = ["x","y"])
        self.ler_obs()
        print(self.meteo)
        print(self.estaticos)
        print(self.dloc)
        
if __name__ == "__main__":
    
    temp = App()
    temp.leituras()