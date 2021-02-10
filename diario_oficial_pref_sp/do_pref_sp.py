# -*- coding: utf-8
# Abraji (https://www.abraji.org.br)
# Reinaldo Chaves (reinaldo@abraji.org.br)
# Programa acessar a API do Diário Oficial da Prefeitura de SP
# Licitações e Publicações
#

'''
Para acessar pode ser seguido este roteiro:

1 – Vá no https://apilib.prefeitura.sp.gov.br/store/ e clique em VÁ PARA A VITRINE DE APIS. Clique depois em Criar Conta. Depois faça o login no site

2 – Entre na Vitrine de APIS e escolha uma delas. Como a API do e-SIC municipal ou a Diario_Oficial-v1

3 – Dentro da API escolha a opção “Inscrever-se”

4 – Clique no menu no alto na esquerda em APLICAÇÕES

5 – Clique em “DefaultApplication”

6 - Clique na aba "Chaves de Produção"

7 – Clique em gerar as chaves. Vão aparecer as chaves: "Chave do Consumidor" e "Segredo do Consumidor" (estas chaves você pode usar no seu script)

(MAS AS CHAVES TÊM CURTA DURAÇÃO DE TEMPO - VOCÊ PRECISA PEGAR NOVAS DEPOIS DE UM TEMPO - AO CLICAR EM 'REGENERAR')

A chave principal usada em scripts é o “Token de Acesso”

8 - Clique de novo no menu no alto na esquerda, agora em APIS – depois VITRINE DE APIS

9 – Entre de novo na API que escolheu no item 2

10 – Na aba Console da API agora você pode testar uma requisição

11 – Clique em GET

12 – Depois em “Try out”

13 – Digite os parâmetros de busca, por exemplo, ano 2018, que é o item obrigatório, e Execute

14 – Abaixo vai aparecer o dado em formato JSON, no caso todos os pedidos de informação feitos à Prefeitura de São Paulo no e-Sic municipal, ou um dia específico no Diario_Oficial-v1
'''


import requests
import pandas as pd
from pprint import pprint
import time


payload = {}

# A key Bearer precisa ser renovada a cada 3.600 segundos em https://apilib.prefeitura.sp.gov.br
# Colocar a sua no xxxxxxxxxxxxxxxxxxxxxx
headers = {
  'accept': 'application/json',
  'Authorization': 'Bearer xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
}



### LICITAÇÕES PUBLICADAS NO DIÁRIO OFICIAL DA PREFEITURA DE SÃO PAULO

# Eexemplo com o mes de janeiro/2021
# Documentacao: https://apilib.prefeitura.sp.gov.br/store/apis/info?name=Diario_Oficial&version=v1&provider=admin#/tab1

for i in range(1,32):
	if i <= 9:
		dia = "0" + str(i)
	else:
		dia = str(i)

	url = "https://gateway.apilib.prefeitura.sp.gov.br/sg/dom/v1/Licitacao?dataPublicacao=2021-01-" + dia + "&caderno=11"

	try:
		response = requests.request("GET", url, headers=headers, data = payload)
	except requests.exceptions.RequestException as e:  # This is the correct syntax
    	raise SystemExit(e)

    codigo = response.status_code

	if codigo != 200:
		print(url)
		print("Erro na data, ou na requisição, ou sem informações na data escolhida: " + str(codigo))
	else:
		dados = response.json()
		#pprint(dados)
		df_procura1 = pd.DataFrame(dados)

		if i == 1:
            df_licit = df_procura1
        else:
            df_licit = df_licit.append(df_procura1)
    
    time.sleep(2)

df_licit.info()

# Salva em CSV
df_licit.to_csv('dados_licitacoes_no_DO_prefeitura_sp_janeiro_2021.csv', index=False)








### PUBLICAÇÕES NO DIÁRIO OFICIAL DA PREFEITURA DE SÃO PAULO

# Eexemplo com o mes de janeiro/2021
# Documentacao: https://apilib.prefeitura.sp.gov.br/store/apis/info?name=Diario_Oficial&version=v1&provider=admin#/tab1

for i in range(1,32):
	if i <= 9:
		dia = "0" + str(i)
	else:
		dia = str(i)

	url = "https://gateway.apilib.prefeitura.sp.gov.br/sg/dom/v1/Publicacao?dataPublicacao=2021-01-" + dia + "&caderno=11"

	try:
		response = requests.request("GET", url, headers=headers, data = payload)
	except requests.exceptions.RequestException as e:  # This is the correct syntax
    	raise SystemExit(e)

    codigo = response.status_code

	if codigo != 200:
		print(url)
		print("Erro na data, ou na requisição, ou sem informações na data escolhida: " + str(codigo))
	else:
		dados = response.json()
		#pprint(dados)
		df_procura1 = pd.DataFrame(dados)

		if i == 1:
            df_publi = df_procura1
        else:
            df_publi = df_publi.append(df_procura1)
    
    time.sleep(2)

df_publi.info()

# Salva em CSV
df_publi.to_csv('dados_publicacoes_no_DO_prefeitura_sp_janeiro_2021.csv', index=False)


