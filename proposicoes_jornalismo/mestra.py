# -*- coding: utf-8
# Abraji (https://www.abraji.org.br)
# Reinaldo Chaves (reinaldo@abraji.org.br)
# Programa acessar as APIs do Senado e da Camara
# Baixas as proposicoes do dia e dia anterior
# Filtra aquelas com palavras-chave sobre o jornalismo
# Envia um e-mail de alerta para endereços de escolha
# 

import requests 
import pandas as pd
import time
from datetime import datetime, timedelta
import os
import json
import xmltodict
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText




### FUNÇÃO DA CÂMARA DOS DEPUTADOS
def camara(dia_anterior,mes_anterior,ano_anterior,dia_hoje,mes_hoje,ano_hoje):
  # Forma url de pesquisa
	url = "https://dadosabertos.camara.leg.br/api/v2/proposicoes?dataInicio=%s-%s-%s&dataFim=%s-%s-%s&ordem=ASC&ordenarPor=id" % (ano_anterior, mes_anterior, dia_anterior, ano_hoje, mes_hoje, dia_hoje)
	print(url)

	# Captura quantas páginas tem esse intervalo de data na API
	parametros = {'formato': 'json', 'itens': 100}
	resposta = requests.get(url, parametros)
    
	for vez in resposta.json()['links']:
		conta = {"rel": vez['rel'].strip(), "href": vez['href'].strip()}

	# Testa se a url tem alguma proposicao
	ultimo = conta['rel']
	if ultimo != 'last':
		column_names = ["a"]
		df = pd.DataFrame(columns = column_names)
		return df

	# Para este item da API da Câmara sempre o último item link (last) tem o número de páginas
	# Considerando 100 itens por página

	# Isola o endereço de last
	link_ultimo = str(conta['href'].strip())

	# Encontra local exato onde termina o número de páginas
	posicao = int(link_ultimo.find('&itens='))

	# Com um fatiamento de lista, a partir da posição 139 onde sempre está o número, captura o número
	# de caracteres que corresponde a "posicao"
	# Exemplo: se "posicao" tiver 141 então vai ser [139:141]
	# o que significa comprimento de 139 (inclusive) até 141 (exclusive)
	# E adiciono mais 1 porque o range abaixo sempre vai um menos
	ultima = int(link_ultimo[139:posicao]) + 1

	# Cria lista vazia
	proposicoes = []

	# Faz a iteração a partir do número de páginas encontrado
	for pagina in range(1, ultima):
  		parametros = {'formato': 'json', 'itens': 100, 'pagina': pagina}
  		resposta = requests.get(url, parametros)

	    # Captura os dados          
	    for vez in resposta.json()['dados']:
        dicionario = {"id": str(vez['id']).strip(), 
                          "uri": str(vez['uri']).strip(), 
                          "siglaTipo": str(vez['siglaTipo']).strip(), 
                          "codTipo": str(vez['codTipo']).strip(), 
                          "numero": str(vez['numero']).strip(), 
                          "ano": str(vez['ano']).strip(), 
                          "ementa": str(vez['ementa']).strip()
                          }
  		  proposicoes.append(dicionario)

	df_proposicoes_api = pd.DataFrame(proposicoes)
	#df_proposicoes_api.info()


	# Isola apenas proposicoes de interesse
	df_proposicoes_api['ementa_copia'] = df_proposicoes_api['ementa']
	df_proposicoes_api['ementa_copia'] = df_proposicoes_api['ementa_copia'].str.upper()

	df_proposicoes_api_final = df_proposicoes_api[pd.notnull(df_proposicoes_api['ementa_copia'])].copy()


	# Coleta autores
	endpoint = "https://www.camara.leg.br/SitCamaraWS/Proposicoes.asmx/ListarAutoresProposicao?codProposicao="

	conta = 0

	for num, row in df_proposicoes_api_final.iterrows():
    id = row['id']

    url = endpoint + id
    #print(url)

    try:
      r = requests.get(url)
    except requests.exceptions.RequestException as e:
    	print("Requests exception: {}".format(e))

    jsonString = json.dumps(xmltodict.parse(r.text), indent=4)

    d = json.loads(jsonString)

    lista = [d['autores']]

    df_lista = pd.DataFrame(lista)
    df_lista["id"] = id
    
    if conta == 0:
      df_autores = df_lista.copy()
    else:
    	df_autores = df_autores.append(df_lista)

    conta = conta + 1
	#df_autores.info()

	seleciona = jornal(df_proposicoes_api_final, 'camara')

  # Testa se há frases no dia 
  tamanho = len(seleciona)
  if tamanho == 0:
    return seleciona

	# Busca a última situação das proposicoes
	endpoint = "https://dadosabertos.camara.leg.br/api/v2/proposicoes/"

	projetos = []
	parametros = {'formato': 'json'}

	for num, row in seleciona.iterrows():
    id = row['id']

  	url = endpoint + id
  	#print(url)

  	# captura os dados de detalhes
  	try:
      r = requests.get(url, parametros)
  	except requests.exceptions.RequestException as e:
    	print("Requests exception: {}".format(e))

  	vez =  r.json()['dados']
    
  	dicionario = {"id": str(vez['id']).strip(), 
        	          "uri": str(vez['uri']).strip(), 
                          "siglaTipo": str(vez['siglaTipo']).strip(), 
                          "codTipo": str(vez['codTipo']).strip(), 
                          "numero": str(vez['numero']).strip(), 
                          "ano": str(vez['ano']).strip(), 
                          "ementa": str(vez['ementa']).strip(),
                          "dataApresentacao": str(vez['dataApresentacao']).strip(),
                          "statusProposicao_dataHora": str(vez['statusProposicao']['dataHora']).strip(),
                          "statusProposicao_siglaOrgao": str(vez['statusProposicao']['siglaOrgao']).strip(),
                          "statusProposicao_siglaOrgao": str(vez['statusProposicao']['siglaOrgao']).strip(),
                          "statusProposicao_descricaoTramitacao": str(vez['statusProposicao']['descricaoTramitacao']).strip(),
                          "statusProposicao_descricaoSituacao": str(vez['statusProposicao']['descricaoSituacao']).strip(),
                          "statusProposicao_despacho": str(vez['statusProposicao']['despacho']).strip(),
                          "keywords": str(vez['keywords']).strip(),
                          "urlInteiroTeor": str(vez['urlInteiroTeor']).strip(),
                          "uriAutores": str(vez['uriAutores']).strip()
                          }

  	projetos.append(dicionario)
    
	df_proposicoes_situacao = pd.DataFrame(projetos)
	# Inclui autores
	df_proposicoes_situacao_autor = pd.merge(df_proposicoes_situacao.drop_duplicates('id'), df_autores, left_on='id', right_on='id')
	#df_projetos_situacao.info()
	

	df_proposicoes_situacao_autor['ementa_minuscula'] = df_proposicoes_situacao_autor['ementa']
	df_proposicoes_situacao_autor['ementa_minuscula'] = df_proposicoes_situacao_autor['ementa_minuscula'].str.lower()

	return df_proposicoes_situacao_autor





### FUNÇÃO DO SENADO
# função para ler todas chaves nas APIs do senado
def get_by_key(key, value):
    try:
        if '.' in key:
            old_key, new_key = key.split('.', 1)
            new_value = value[old_key]
            return get_by_key(new_key, new_value)
        else:
            return value[key]
    except (KeyError, TypeError) as _:
        return None


def senado(ano_anterior, mes_anterior, dia_anterior):
  # Define header padrão
	headers = {"Accept" : "application/json"}

	# Forma url de pesquisa principal
	url = "http://legis.senado.leg.br/dadosabertos/materia/tramitando?data=%s%s%s" % (ano_anterior, mes_anterior, dia_anterior)
	print(url)

	tramitando = []

	try:
    r = requests.get(url, headers=headers)
    tramit = r.json()
	except requests.exceptions.RequestException as e:
    print("Requests exception: {}".format(e))

  # Testa se a url tem alguma proposicao
  try:
    teste = str(tramit["ListaMateriasTramitando"]["Materias"]["Materia"])
  except KeyError:
   	column_names = ["a"]
		df = pd.DataFrame(columns = column_names)
		return df
  except TypeError:
    column_names = ["a"]
		df = pd.DataFrame(columns = column_names)
		return df

  # Captura dados de proposicoes tramitando
	for item in tramit["ListaMateriasTramitando"]["Materias"]["Materia"]:
    dicionario = {
        		"CodigoMateria": get_by_key('IdentificacaoMateria.CodigoMateria', item),
        		"SiglaCasaIdentificacaoMateria": get_by_key('IdentificacaoMateria.SiglaCasaIdentificacaoMateria', item),
        		"NomeCasaIdentificacaoMateria": get_by_key('IdentificacaoMateria.NomeCasaIdentificacaoMateria', item),
        		"SiglaSubtipoMateria": get_by_key('IdentificacaoMateria.SiglaSubtipoMateria', item),
        		"DescricaoSubtipoMateria": get_by_key('IdentificacaoMateria.DescricaoSubtipoMateria', item),
        		"NumeroMateria": get_by_key('IdentificacaoMateria.NumeroMateria', item),
        		"AnoMateria": get_by_key('IdentificacaoMateria.AnoMateria', item),
        		"DescricaoIdentificacaoMateria": get_by_key('IdentificacaoMateria.DescricaoIdentificacaoMateria', item),
        		"IndicadorTramitando": get_by_key('IdentificacaoMateria.IndicadorTramitando', item),
        		"DataUltimaAtualizacao": get_by_key('DataUltimaAtualizacao', item)
        		}

    tramitando.append(dicionario)

	df_tramitando = pd.DataFrame(tramitando)
	#df_tramitando.info()

	#df_tramitando.to_csv('resultados/senado/proposicoes_senado_do_dia.csv',index=False)


	# Dados de cada materia
	prefixo = 'http://legis.senado.leg.br/dadosabertos/materia/'

	projetos_det = []

	for num, row in df_tramitando.iterrows():
    codigo = row['CodigoMateria']

   	url = prefixo + codigo
    		#print(url)
    
    try:
      r = requests.get(url, headers=headers)
    except requests.exceptions.HTTPError as errh:
      print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
      print ("Error Connecting:",errc) 
    except requests.exceptions.Timeout as errt:
      print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
      print ("OOps: Something Else",err)

    projects = r.json()
    
    dicionario = {
        		"CodigoMateria": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.CodigoMateria', projects),
        		"SiglaCasaIdentificacaoMateria": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.SiglaCasaIdentificacaoMateria', projects),
        		"NomeCasaIdentificacaoMateria": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.NomeCasaIdentificacaoMateria', projects),
        		"SiglaSubtipoMateria": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.SiglaSubtipoMateria', projects),
        		"DescricaoSubtipoMateria": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.DescricaoSubtipoMateria', projects),
        		"NumeroMateria": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.NumeroMateria', projects),
        		"AnoMateria": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.AnoMateria', projects),
        		"DescricaoObjetivoProcesso": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.DescricaoObjetivoProcesso', projects),
        		"DescricaoIdentificacaoMateria": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.DescricaoIdentificacaoMateria', projects),
        		"IndicadorTramitando": get_by_key('DetalheMateria.Materia.IdentificacaoMateria.IndicadorTramitando', projects),
        		"EmentaMateria": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.EmentaMateria', projects),
        		"ExplicacaoEmentaMateria": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.ExplicacaoEmentaMateria', projects),
        		"ApelidoMateria": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.ApelidoMateria', projects),
        		"IndicadorComplementar": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.IndicadorComplementar', projects),
        		"DataApresentacao": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.DataApresentacao', projects),
        		"DataLeitura": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.DataLeitura', projects),
        		"SiglaCasaLeitura": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.SiglaCasaLeitura', projects),
        		"NomeCasaLeitura": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.NomeCasaLeitura', projects),        
        		"CodigoNatureza": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.NaturezaMateria.CodigoNatureza', projects),        
        		"NomeNatureza": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.NaturezaMateria.NomeNatureza', projects),        
        		"DescricaoNatureza": get_by_key('DetalheMateria.Materia.DadosBasicosMateria.NaturezaMateria.DescricaoNatureza', projects),        
        		"Codigo_assunto": get_by_key('DetalheMateria.Materia.Assunto.AssuntoEspecifico.Codigo', projects),                                                
        		"Descricao_assunto": get_by_key('DetalheMateria.Materia.Assunto.AssuntoEspecifico.Descricao', projects),                                                        
        		"Codigo_assunto_geral": get_by_key('DetalheMateria.Materia.Assunto.AssuntoGeral.Codigo', projects),                                                                
        		"Descricao_assunto_geral": get_by_key('DetalheMateria.Materia.Assunto.AssuntoGeral.Descricao', projects),                                                                 
        		"NomePoderOrigem": get_by_key('DetalheMateria.Materia.OrigemMateria.NomePoderOrigem', projects),
        		"SiglaCasaOrigem": get_by_key('DetalheMateria.Materia.OrigemMateria.SiglaCasaOrigem', projects),        
        		"NomeCasaOrigem": get_by_key('DetalheMateria.Materia.OrigemMateria.NomeCasaOrigem', projects),        
        		"SiglaCasaIniciadora": get_by_key('DetalheMateria.Materia.CasaIniciadoraNoLegislativo.SiglaCasaIniciadora', projects),        
        		"NomeCasaIniciadora": get_by_key('DetalheMateria.Materia.CasaIniciadoraNoLegislativo.NomeCasaIniciadora', projects)
                   	}
     
    try:
      NomeAutor = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['NomeAutor'])
    except KeyError:
      NomeAutor = None                
    except TypeError:
      NomeAutor = None   

    try:
      SiglaTipoAutor = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['SiglaTipoAutor'])
    except KeyError:
      SiglaTipoAutor = None                
    except TypeError:
     SiglaTipoAutor = None  
        
    try:
        DescricaoTipoAutor = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['DescricaoTipoAutor'])
    except KeyError:
        DescricaoTipoAutor = None                
    except TypeError:
        DescricaoTipoAutor = None  

    try:
        UfAutor = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['UfAutor'])
    except KeyError:
        UfAutor = None                
    except TypeError:
        UfAutor = None  

		try:
      NumOrdemAutor = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['NumOrdemAutor'])
    except KeyError:
      NumOrdemAutor = None                
    except TypeError:
      NumOrdemAutor = None  

    try:
      IndicadorOutrosAutores = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IndicadorOutrosAutores'])
    except KeyError:
      IndicadorOutrosAutores = None                
    except TypeError:
      IndicadorOutrosAutores = None  

    try:
      CodigoParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['CodigoParlamentar'])
    except KeyError:
      CodigoParlamentar = None                
    except TypeError:
      CodigoParlamentar = None  

    try:
      CodigoPublicoNaLegAtual = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['CodigoPublicoNaLegAtual'])
    except KeyError:
      CodigoPublicoNaLegAtual = None                
    except TypeError:
      CodigoPublicoNaLegAtual = None  

    try:
      NomeParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['NomeParlamentar'])
    except KeyError:
      NomeParlamentar = None                
    except TypeError:
      NomeParlamentar = None 

    try:
      NomeCompletoParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['NomeCompletoParlamentar'])
    except KeyError:
      NomeCompletoParlamentar = None                
    except TypeError:
     	NomeCompletoParlamentar = None 

    try:
      SexoParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['SexoParlamentar'])
    except KeyError:
      SexoParlamentar = None                
    except TypeError:
      SexoParlamentar = None 

    try:
      FormaTratamento = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['FormaTratamento'])
    except KeyError:
      FormaTratamento = None                
    except TypeError:
      FormaTratamento = None 

    try:
    	UrlFotoParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['UrlFotoParlamentar'])
    except KeyError:
    	UrlFotoParlamentar = None                
    except TypeError:
     	UrlFotoParlamentar = None 

		try:
      UrlPaginaParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['UrlPaginaParlamentar'])
    except KeyError:
    	UrlPaginaParlamentar = None                
    except TypeError:
    	UrlPaginaParlamentar = None 

		try:
      EmailParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['EmailParlamentar'])
    except KeyError:
      EmailParlamentar = None                
    except TypeError:
      EmailParlamentar = None 

    try:
      SiglaPartidoParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['SiglaPartidoParlamentar'])
    except KeyError:
      SiglaPartidoParlamentar = None                
    except TypeError:
      SiglaPartidoParlamentar = None 

    try:
      UfParlamentar = str(projects['DetalheMateria']['Materia']['Autoria']['Autor'][0]['IdentificacaoParlamentar']['UfParlamentar'])
    except KeyError:
      UfParlamentar = None                
    except TypeError:
      UfParlamentar = None 

    try:	
      NumeroAutuacao = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['NumeroAutuacao'])
    except KeyError:
      NumeroAutuacao = None                
    except TypeError:
      NumeroAutuacao = None 

    try:
      DataSituacao = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Situacao']['DataSituacao'])
    except KeyError:
      DataSituacao = None                
    except TypeError:
      DataSituacao = None 

    try:
      CodigoSituacao = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Situacao']['CodigoSituacao'])
    except KeyError:
      CodigoSituacao = None                
    except TypeError:
      CodigoSituacao = None

    try:
      SiglaSituacao = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Situacao']['SiglaSituacao'])
    except KeyError:
      SiglaSituacao = None                
    except TypeError:
      SiglaSituacao = None

    try:
      DescricaoSituacao = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Situacao']['DescricaoSituacao'])
    except KeyError:
      DescricaoSituacao = None                
    except TypeError:
      DescricaoSituacao = None

    try:
      DataLocal = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Local']['DataLocal'])
    except KeyError:
      DataLocal = None                
    except TypeError:
      DataLocal = None

    try:
      CodigoLocal = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Local']['CodigoLocal'])
    except KeyError:
      CodigoLocal = None                
    except TypeError:
      CodigoLocal = None

    try:
      TipoLocal = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Local']['TipoLocal'])
    except KeyError:
      TipoLocal = None                
    except TypeError:
      TipoLocal = None
        
    try:
      SiglaCasaLocal = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Local']['SiglaCasaLocal'])
    except KeyError:
      SiglaCasaLocal = None                
    except TypeError:
      SiglaCasaLocal = None

    try:
      NomeCasaLocal = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Local']['NomeCasaLocal'])
    except KeyError:
      NomeCasaLocal = None                
    except TypeError:
      NomeCasaLocal = None

    try:
      SiglaLocal = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Local']['SiglaLocal'])
    except KeyError:
      SiglaLocal = None                
    except TypeError:
      SiglaLocal = None

    try:
      NomeLocal = str(projects['DetalheMateria']['Materia']['SituacaoAtual']['Autuacoes']['Autuacao'][0]['Local']['NomeLocal'])
    except KeyError:
      NomeLocal = None                
    except TypeError:
      NomeLocal = None

    try:
      url_emendas = str(projects['DetalheMateria']['Materia']['OutrasInformacoes']['Servico'][0]['UrlServico'])
    except KeyError:
      url_emendas = None                
    except TypeError:
      url_emendas = None

    try:
      url_movimentacoes = str(projects['DetalheMateria']['Materia']['OutrasInformacoes']['Servico'][1]['UrlServico'])
    except KeyError:
      url_movimentacoes = None                
    except TypeError:
      url_movimentacoes = None

    try:
      url_relatorias = str(projects['DetalheMateria']['Materia']['OutrasInformacoes']['Servico'][2]['UrlServico'])
    except KeyError:
      url_relatorias = None                
    except TypeError:
      url_relatorias = None

    try:
      url_texto = str(projects['DetalheMateria']['Materia']['OutrasInformacoes']['Servico'][3]['UrlServico'])
    except KeyError:
      url_texto = None                
    except TypeError:
      url_texto = None

    try:
      url_votacoes_materia = str(projects['DetalheMateria']['Materia']['OutrasInformacoes']['Servico'][4]['UrlServico'])
    except KeyError:
      url_votacoes_materia = None                
    except TypeError:
      url_votacoes_materia = None

    try:
      url_votacoes_comissoes = str(projects['DetalheMateria']['Materia']['OutrasInformacoes']['Servico'][5]['UrlServico'])
    except KeyError:
      url_votacoes_comissoes = None                
    except TypeError:
      url_votacoes_comissoes = None

    dicionario['NomeAutor'] = NomeAutor
    dicionario['SiglaTipoAutor'] = SiglaTipoAutor
    dicionario['DescricaoTipoAutor'] = DescricaoTipoAutor
    dicionario['UfAutor'] = UfAutor
    dicionario['NumOrdemAutor'] = NumOrdemAutor
    dicionario['IndicadorOutrosAutores'] = IndicadorOutrosAutores
    dicionario['CodigoParlamentar'] = CodigoParlamentar
    dicionario['CodigoPublicoNaLegAtual'] = CodigoPublicoNaLegAtual
    dicionario['NomeParlamentar'] = NomeParlamentar
    dicionario['NomeCompletoParlamentar'] = NomeCompletoParlamentar
    dicionario['SexoParlamentar'] = SexoParlamentar
    dicionario['FormaTratamento'] = FormaTratamento
    dicionario['UrlFotoParlamentar'] = UrlFotoParlamentar
    dicionario['UrlPaginaParlamentar'] = UrlPaginaParlamentar
    dicionario['EmailParlamentar'] = EmailParlamentar
    dicionario['SiglaPartidoParlamentar'] = SiglaPartidoParlamentar
    dicionario['UfParlamentar'] = UfParlamentar
    dicionario['NumeroAutuacao'] = NumeroAutuacao
    dicionario['DataSituacao'] = DataSituacao
    dicionario['CodigoSituacao'] = CodigoSituacao
    dicionario['SiglaSituacao'] = SiglaSituacao
    dicionario['DescricaoSituacao'] = DescricaoSituacao
    dicionario['DataLocal'] = DataLocal
    dicionario['CodigoLocal'] = CodigoLocal
    dicionario['TipoLocal'] = TipoLocal
    dicionario['SiglaCasaLocal'] = SiglaCasaLocal
    dicionario['NomeCasaLocal'] = NomeCasaLocal
    dicionario['SiglaLocal'] = SiglaLocal
    dicionario['NomeLocal'] = NomeLocal
    dicionario['url_emendas'] = url_emendas
    dicionario['url_movimentacoes'] = url_movimentacoes
    dicionario['url_relatorias'] = url_relatorias
    dicionario['url_texto'] = url_texto
    dicionario['url_votacoes_materia'] = url_votacoes_materia
    dicionario['url_votacoes_comissoes'] = url_votacoes_comissoes


    projetos_det.append(dicionario)

	df_propdia_det = pd.DataFrame(projetos_det)
	df_propdia_det = df_propdia_det[pd.notnull(df_propdia_det['EmentaMateria'])].copy()
	#df_propdia_det.info()


	# Captura link do inteiro teor
	prefixo = 'http://legis.senado.leg.br/dadosabertos/materia/textos/'

	prop_teor = []

	for num, row in df_propdia_det.iterrows():
    codigo = row['CodigoMateria']

		url = prefixo + codigo
    #print(url)
    
    try:
      r = requests.get(url, headers=headers)
    except requests.exceptions.HTTPError as errh:
    	print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
    	print ("Error Connecting:",errc) 
    except requests.exceptions.Timeout as errt:
    	print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
    	print ("OOps: Something Else",err)

    projects = r.json()
    
    dicionario = {
        		"CodigoMateria": get_by_key('TextoMateria.Materia.IdentificacaoMateria.CodigoMateria', projects)}

	  try:
      CodigoTexto = str(projects['TextoMateria']['Materia']['Textos']['Texto'][0]['CodigoTexto'])
    except KeyError:
    	CodigoTexto = None                
    except TypeError:
      CodigoTexto = None

    try:
      UrlTexto = str(projects['TextoMateria']['Materia']['Textos']['Texto'][0]['UrlTexto'])
    except KeyError:
      UrlTexto = None                
    except TypeError:
      UrlTexto = None

    dicionario['CodigoTexto'] = CodigoTexto
    dicionario['UrlTexto'] = UrlTexto

    prop_teor.append(dicionario)

	df_prop_teor = pd.DataFrame(prop_teor)
	#df_prop_teor.info()

	# Une os dois dataframes
	df_proposicoes = pd.merge(df_propdia_det, df_prop_teor, left_on='CodigoMateria', right_on='CodigoMateria')
	#df_proposicoes.info()
	#df_proposicoes.to_csv('resultados/senado/proposicoes_senado_detalhes_do_dia.csv',index=False)


	# Isola apenas proposicoes de interesse
	df_proposicoes['ementa_copia'] = df_proposicoes['EmentaMateria']
	df_proposicoes['ementa_copia'] = df_proposicoes['ementa_copia'].str.upper()
	df_proposicoes['ementa_minuscula'] = df_proposicoes['EmentaMateria']
	df_proposicoes['ementa_minuscula'] = df_proposicoes['EmentaMateria'].str.lower()

	seleciona = jornal(df_proposicoes, 'senado')
	#seleciona.info()
	
	return seleciona





### FUNÇÃO PARA TERMOS DE INTERESSE
def jornal(dados, origem):
	# Define termos de interesse
	search_list = ["JORNALISMO", "JORNALISTA", "JORNALISTAS", "COMUNICADORES", "IMPRENSA", "VERIFICADORES DE FATOS", "CHECAGEM DE FATOS", "FAKE NEWS", "DESINFORMAÇÃO", "TRANSPARÊNCIA NA INTERNET", "RADIODIFUSÃO", "LIBERDADE DE EXPRESSÃO"]

	mask = dados['ementa_copia'].str.contains('|'.join(search_list))
	seleciona = dados[mask]
	return seleciona




### CRIA FRASES
def frases(dados, origem):
  lista_sentencas = []
  #dados.info()
	conta = 1
	for num, row in dados.iterrows():

		if origem == 'senado':
    			proposicao_ementa = row['ementa_minuscula']
    			proposicao_tipo = row['SiglaSubtipoMateria']
    			proposicao_numero = row['NumeroMateria']
    			proposicao_ano = row['AnoMateria']
    			tramitacao = row['NomeLocal']
    			status = row['DescricaoSituacao']
    			endereco = row['UrlTexto']
    			nome = row['NomeAutor']
    			casa = 'SENADO'
          pagina = "https://www25.senado.leg.br/web/atividade/materias/-/materia/" + str(row['CodigoMateria'])
    elif origem == 'camara':
    			proposicao_ementa = row['ementa_minuscula']
    			proposicao_tipo = row['siglaTipo']
    			proposicao_numero = row['numero']
    			proposicao_ano = row['ano']
    			tramitacao = row['statusProposicao_descricaoTramitacao']
    			status = row['statusProposicao_descricaoSituacao']
    			endereco = row['urlInteiroTeor']
    			nome = str(row['autor']).replace("[", "")
    			nome = nome.replace("]", "")
    			nome = nome.replace("'", "")
    			casa = 'CÂMARA'
          pagina = "https://www.camara.leg.br/propostas-legislativas/" + str(row['id'])

    sentencas = {}

    if 'jornalismo' in proposicao_ementa:
      sentencas['texto3/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre jornalismo e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'
    elif 'jornalista' in proposicao_ementa or 'jornalistas' in proposicao_ementa:
      sentencas['texto4/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre jornalistas e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'
    elif 'comunicadores' in proposicao_ementa:
      sentencas['texto5/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre ccomunicadores e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'
    elif 'imprensa' in proposicao_ementa:
      sentencas['texto6/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre imprensa e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'
    elif 'desinformação' in proposicao_ementa:
      sentencas['texto11/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre desinformação e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'
    elif 'notícias falsas' in proposicao_ementa or 'fake news' in proposicao_ementa:
      sentencas['texto7/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre fake news ou notícias falsas e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'
    elif 'verificadores de fatos' in proposicao_ementa or 'checagem de fatos' in proposicao_ementa:
      sentencas['texto8/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre verificadores de fatos ou checagem de fatos e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'
    elif 'transparência na internet' in proposicao_ementa:
      sentencas['texto9/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre transparência na internet e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'
    elif 'radiodifusão' in proposicao_ementa:
      sentencas['texto10/' + str(conta)] = f'{casa}: {proposicao_tipo} {proposicao_numero}/{proposicao_ano}, de autoria de {nome}, fala sobre radiodifusão e sofreu alterações em sua tramitação. Tramitação: {tramitacao}. Situação: {status}. Página: {pagina}. Teor: {endereco}'

    
    #print(sentencas)
    # Testa se dicionario veio vazio
    res = not bool(sentencas)  
    if res == False:
      lista_sentencas.append(sentencas)

    	#print(lista_sentencas)
    conta = conta + 1 

    #print(lista_sentencas)
	df_lista_sentencas = pd.DataFrame(lista_sentencas)
	#df_lista_sentencas.info()
	#df_lista_sentencas.to_csv('teste_sen2.csv',index=False)
    	#df_lista_sentencas.info()
    	#print(df_lista_sentencas)

  with open('resultados/tweets.json', 'w') as outfile:
    json.dump(lista_sentencas, outfile)


  return df_lista_sentencas





### MANDA E-MAIL
def mandamail(dados):
  now = datetime.now()
  dia_hoje = now.strftime("%d")
  mes_hoje = now.strftime("%m")
  ano_hoje = now.strftime("%Y")

  recipients = ['reinaldo@abraji.org.br']
  msg = MIMEMultipart()
  msg['From'] = "Robot jornalista"  # sender name
  msg['To'] = ", ".join(recipients) # for one recipient just enter a valid email address
  msg['Subject'] = str(dia_hoje) + "/" + str(mes_hoje) + "/" + str(ano_hoje) + " Tramitacoes de interesse do jornalismo no Congresso"
	
  # Isola apenas primeiras linhas
	df = dados.bfill().iloc[[0]]
	columns = list(df) 

	# Itera nas colunas de cada frase
  lista = []
	for i in columns:
		texto = df[i][0]
    if texto != None:
      lista.append(texto)
  #print(lista)

  body = "Olá seres humanos!\n\nEu sou um robô que vasculha as APIs da Câmara e do Senado em busca de proposições de interesse dos jornalistas.\n\nVeja as que tiveram alguma tramitação entre hoje e anteontem (todo dia eu vasculho esse intervalo):\n\n" + '\n'.join(lista)+ "\n\nNo momento eu procuro estas palavras-chave JORNALISMO, JORNALISTA, JORNALISTAS, COMUNICADORES, IMPRENSA, VERIFICADORES DE FATOS, CHECAGEM DE FATOS, FAKE NEWS, DESINFORMAÇÃO, TRANSPARÊNCIA NA INTERNET. Posso procurar quantas quiserem.\n\nPara mais detalhes consulte meu mestre: reinaldo@abraji.org.br"

  msg.attach(MIMEText(body, 'plain'))
  server = smtplib.SMTP('smtp.gmail.com', 587)  # put your relevant SMTP here

  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login('seuemail', 'suasenha')   # use your real gmail account user name and password
  server.send_message(msg)
  server.quit()


  return





### DEFINIR BLOCO DE EXECUÇÃO PRINCIPAL
def main():

	# Captura o dia, mês e ano de ontem
	dia_anterior = (datetime.now() - timedelta(1)).strftime('%d')
	mes_anterior = (datetime.now() - timedelta(1)).strftime('%m')
	ano_anterior = (datetime.now() - timedelta(1)).strftime('%Y')

	# Captura o dia, mês e ano de hoje
	now = datetime.now()
	dia_hoje = now.strftime("%d")
	mes_hoje = now.strftime("%m")
	ano_hoje = now.strftime("%Y")

	#Captura proposicoes Camara
	prop_cam = camara(dia_anterior,mes_anterior,ano_anterior,dia_hoje,mes_hoje,ano_hoje)
	tamanho = len(prop_cam.index)
  print("Quantidade de proposicoes de interesse na Camara: ", tamanho)
  prop_cam.info()

  # Cria frases da Camara
  if tamanho != 0:
    nome = "resultados/" + dia_anterior + "_" + mes_anterior + "_" + ano_anterior + "_" + "proposicoes_camara_jornalismo"
    prop_cam.to_csv(f'{nome}.csv',index=False)

    df_lista_sentencas = frases(prop_cam, 'camara')
   	#print(df_lista_sentencas)
    #a = input("-----------------")

   	# Manda e-mail
   	tam_frases = len(df_lista_sentencas.index)
   	if tam_frases > 0:
      mandamail(df_lista_sentencas)

  print("/////////////////////////////////////")  	

  # Captura proposicoes Senado
	prop_sen = senado(ano_anterior, mes_anterior, dia_anterior)
	tamanho = len(prop_sen.index)
  print("Quantidade de proposicoes de interesse no Senado: ", tamanho)
  #prop_sen.info()
	
	# Cria frases do Senado
  if tamanho != 0:
    nome = "resultados/" + dia_anterior + "_" + mes_anterior + "_" + ano_anterior + "_" + "proposicoes_senado_jornalismo"
    prop_sen.to_csv(f'{nome}.csv',index=False)

    df_lista_sentencas = frases(prop_sen, 'senado')
   	#print(df_lista_sentencas)

   	# Manda e-mail
   	tam_frases = len(df_lista_sentencas.index)
   	if tam_frases > 0:
      mandamail(df_lista_sentencas)



# executar bloco principal
if __name__ == '__main__':
	main()


