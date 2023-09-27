#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 15:37:32 2023

@author: felipe.bortolletto

Programa com classe responsavel para rodar a calibração em si


"""

import xml.etree.ElementTree as ET


class Altera_Xml():
    
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

        lfuser_element = root.find('lfuser')
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
                    textvar_element.set('value', novo_ano + "-01-01 00:00")
                    self.data_inicial = novo_ano + "-01-01 00:00"
                elif var_nome == "StepEnd":
                    if final_ano == "2023":
                        textvar_element.set('value', "2023-07-04 00:00")
                        self.data_final = "2023-04-07 00:00"
                    else:
                        textvar_element.set('value', final_ano + "-12-31 00:00")
                        self.data_final = final_ano + "-12-31 00:00"

        
        tree.write(arquivo_xml)



    