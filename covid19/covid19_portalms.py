# -*- coding: utf-8
# Abraji (https://www.abraji.org.br)
# Reinaldo Chaves (reinaldo@abraji.org.br)
# 
# Dia 26/03/2020
#
# Captura dados da covid-19 disponibilizados pelo Ministério da Saúde em https://covid.saude.gov.br/
#


import requests
import pandas as pd


# CAPTURA CASOS POR REGIOES
headers = {
    'authority': 'xx9p7hp1p7.execute-api.us-east-1.amazonaws.com',
    'accept': 'application/json, text/plain, */*',
    'sec-fetch-dest': 'empty',
    'x-parse-application-id': 'unAFkcaNDeXajurGB7LChj8SgQYS2ptm',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'origin': 'https://covid.saude.gov.br',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'referer': 'https://covid.saude.gov.br/',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,it;q=0.5',
}

response = requests.get('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalRegiao', headers=headers)

regioes = response.json()

conteudo = []
for pagina in regioes["results"]:
    dicionario = {
                "objectId": pagina.get('objectId'), 
                "nome": pagina.get('nome'), 
                "color": pagina.get('color'), 
                "percent": pagina.get('percent'), 
                "qtd": pagina.get('qtd'), 
                "createdAt": pagina.get('createdAt'), 
                "updatedAt": pagina.get('updatedAt')
                }

    conteudo.append(dicionario)

df_regioes = pd.DataFrame(conteudo)
df_regioes.to_csv('casos_regioes.csv',index=False)



# CAPTURA ACUMULO
headers = {
    'authority': 'xx9p7hp1p7.execute-api.us-east-1.amazonaws.com',
    'accept': 'application/json, text/plain, */*',
    'sec-fetch-dest': 'empty',
    'x-parse-application-id': 'unAFkcaNDeXajurGB7LChj8SgQYS2ptm',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'origin': 'https://covid.saude.gov.br',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'referer': 'https://covid.saude.gov.br/',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,it;q=0.5',
}

response = requests.get('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalAcumulo', headers=headers)

acumulo = response.json()

conteudo = []
for pagina in acumulo["results"]:
    dicionario = {
                "objectId": pagina.get('objectId'), 
                "label": pagina.get('label'), 
                "qtd_confirmado": pagina.get('qtd_confirmado'), 
                "qtd_obito": pagina.get('qtd_obito'), 
                "createdAt": pagina.get('createdAt'), 
                "updatedAt": pagina.get('updatedAt')
                }

    conteudo.append(dicionario)

df_acumulado = pd.DataFrame(conteudo)
df_acumulado.to_csv('casos_acumulados.csv',index=False)


