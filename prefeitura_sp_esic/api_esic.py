# -*- coding: utf-8
# Abraji (https://www.abraji.org.br)
# Reinaldo Chaves (reinaldo@abraji.org.br)
# Programa acessar a API do e-SIC da Prefeitura de SP
#

import requests
import pandas as pd

# Coloque o valor de sua chave Bearer aqui
key      = ''
endpoint = 'https://gateway.apilib.prefeitura.sp.gov.br/cgm/esic/v1/'
headers  = {'Authorization': 'Bearer ' + key}

# Escolha o ano
ano = '2019'

# O limite máximo de resultados que consegui foram 30.000 para o ano de 2019
# A paginação offset ainda não funcionou
# Para outros anos tem que testar o limite - 2018 por exemplo funcionou 40000
limite = '?limite=30000'

# Faz a requisição
r = requests.get(endpoint + ano + limite, headers = headers)

# Pega os dados retornados em JSON
# Faz uma lista a partir de 'data' onde estão os dados
dados = r.json()
lista = dados['data']

# Cria dataframe
df_esic = pd.DataFrame(lista)

df_esic.info()

df_esic.reset_index().head()

# Salva em CSV
df_esic.to_csv('dados_esic2019.csv', index=False)
