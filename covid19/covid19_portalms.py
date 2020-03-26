# -*- coding: utf-8
# Abraji (https://www.abraji.org.br)
# Reinaldo Chaves (reinaldo@abraji.org.br)
# 
# Dia 26/03/2020
#
# Captura dados da covid-19 disponibilizados pelo Ministério da Saúde em https://covid.saude.gov.br/
#

# Instale:
# pip3 install requests
# pip3 install pandas
# pip3 install xlrd
# pip3 install openpyxl


import requests
import pandas as pd

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


# CAPTURA CASOS POR REGIOES
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

# Escolha salvar em CSV ou XLSX
df_regioes.to_csv('casos_regioes.csv',index=False)
df_regioes.to_excel('casos_regioes.xlsx', sheet_name='Sheet1', index=False)



# CAPTURA ACUMULO - DIAS
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

# Escolha salvar em CSV ou XLSX
df_acumulado.to_csv('casos_acumulados.csv',index=False)
df_acumulado.to_excel('casos_acumulados.xlsx', sheet_name='Sheet1', index=False)


# CAPTURA POR ESTADOS
response = requests.get('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalMapa', headers=headers)

estados = response.json()

conteudo = []

for pagina in estados["results"]:
    dicionario = {
                "objectId": pagina.get('objectId'), 
                "nome": pagina.get('nome'), 
                "qtd_confirmado": pagina.get('qtd_confirmado'), 
                "latitude": pagina.get('latitude'), 
                "longitude": pagina.get('longitude'), 
                "createdAt": pagina.get('createdAt'), 
                "updatedAt": pagina.get('updatedAt')
                }

    conteudo.append(dicionario)

df_estados = pd.DataFrame(conteudo)

# Escolha salvar em CSV ou XLSX
df_estados.to_csv('casos_estados.csv',index=False)
df_estados.to_excel('casos_estados.xlsx', sheet_name='Sheet1', index=False)



# CAPTURA POR SEMANA EPIDEMIOLÓGICA
response = requests.get('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalSemana', headers=headers)

semanas = response.json()

conteudo = []

for pagina in semanas["results"]:
    dicionario = {
                "objectId": pagina.get('objectId'), 
                "label": pagina.get('label'), 
                "qtd_confirmado": pagina.get('qtd_confirmado'), 
                "qtd_obito": pagina.get('qtd_obito'), 
                "createdAt": pagina.get('createdAt'), 
                "updatedAt": pagina.get('updatedAt')
                }

    conteudo.append(dicionario)

df_semanas = pd.DataFrame(conteudo)

# Escolha salvar em CSV ou XLSX
df_semanas.to_csv('casos_semanas.csv',index=False)
df_semanas.to_excel('casos_semanas.xlsx', sheet_name='Sheet1', index=False)



# CAPTURA POR DIAS
response = requests.get('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalDias', headers=headers)

dias = response.json()

conteudo = []

for pagina in dias["results"]:
    dicionario = {
                "objectId": pagina.get('objectId'), 
                "label": pagina.get('label'), 
                "qtd_confirmado": pagina.get('qtd_confirmado'), 
                "createdAt": pagina.get('createdAt'), 
                "updatedAt": pagina.get('updatedAt')
                }

    conteudo.append(dicionario)

df_dias = pd.DataFrame(conteudo)

# Escolha salvar em CSV ou XLSX
df_dias.to_csv('casos_dias.csv',index=False)
df_dias.to_excel('casos_dias.xlsx', sheet_name='Sheet1', index=False)




# CAPTURA GERAL - DA SOMA TOTAL
response = requests.get('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalGeral', headers=headers)

geral = response.json()

conteudo = []

for pagina in geral["results"]:
    dicionario = {
                "objectId": pagina.get('objectId'), 
                "total_confirmado": pagina.get('total_confirmado'), 
                "createdAt": pagina.get('createdAt'), 
                "total_obitos": pagina.get('total_obitos'),
                "versao": pagina.get('versao'),
                "dt_atualizacao": pagina.get('dt_atualizacao'),
                }

    conteudo.append(dicionario)

df_geral = pd.DataFrame(conteudo)

# Escolha salvar em CSV ou XLSX
df_geral.to_csv('casos_geral.csv',index=False)
df_geral.to_excel('casos_geral.xlsx', sheet_name='Sheet1', index=False)
