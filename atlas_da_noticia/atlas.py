# -*- coding: utf-8
# Abraji (https://www.abraji.org.br)
# Reinaldo Chaves (reinaldo@abraji.org.br)
# Programa acessar a API do Atlas da Notícia (https://www.atlas.jor.br/)
# É necessário antes se cadastrar, veja como aqui: https://www.atlas.jor.br/plataforma/utilizarAPI/
#

import requests
import pandas as pd

# Link da requisição principal
url = "https://api.atlas.jor.br/api/v1/auth/login"

# Informações de autentificação
payload = "{\"email\": \"coloque_seu_email\", \"password\": \"coloque_sua_senha\"}"

# Parâmetros padrão da API
headers = {
    'Content-Type': "application/json",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Host': "api.atlas.jor.br",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

# Faz a requisição para obter a senha Bearer 
try:
    response = requests.request("POST", url, data=payload, headers=headers)
except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc) 
except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
except requests.exceptions.RequestException as err:
    print ("OOps: Something Else",err)


# Captura a informação exata
body = json.loads(response.content)
# O token
token = body["access_token"]
# O tempo de duração do token
expiresIn = body["expires_in"]

# Agora com a senha é possível fazer diversas requisições
# Exemplo veículos do Estado de SP
# Outros tipos de buscas aqui: https://api.atlas.jor.br/docs
url= "https://api.atlas.jor.br/api/v1/data/analytic?estado=SP"

# Faz a requisição, já informando a senha Bearer
try:
    r = requests.get(url, headers = {"Authorization":"Bearer " + token})
except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc) 
except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
except requests.exceptions.RequestException as err:
    print ("OOps: Something Else",err)

# Lê a resposta em JSON
dados = r.json()

# Cria dataframe
df_atlas = pd.DataFrame(dados)
df_atlas.info()
df_atlas.to_csv('resultados/atlas_sp.csv', index=False)
