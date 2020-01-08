# -*- coding: utf-8
# Abraji (https://www.abraji.org.br)
# Reinaldo Chaves (reinaldo@abraji.org.br)
# Script exemplo de uso do rsiconfi
# Baixa gastos com saúde de municípios de MG com Legislativo e Administração
#

#install.packages("devtools")
#devtools::install_github("tchiluanda/rsiconfi")

library(rsiconfi)
library(dplyr)
library(tidyr)


# Códigos de UFs do Brasil
# https://atendimento.tecnospeed.com.br/hc/pt-br/articles/360021494734-Tabela-de-C%C3%B3digo-de-UF-do-IBGE
# Minas Gerais é 31 - entity

# Vamos ver Despesas por Função (I-E)
# A função get_account_dca retorna os códigos possíveis
# Coloco o ano 2018, o I-E e um código relacionado com MG
# Aqui a lista de todos:
# https://siconfi.tesouro.gov.br/siconfi/pages/public/conteudo/conteudo.jsf?id=581 clique em Tabela dos códigos de instituição utilizados no Siconfi - Código das Instituições

df_conta_dca <- get_account_dca(2018, "I-E", c("31") )

# Cria um vetor com códigos sobre Legislativo e Administração
contas_sel <- c("01", #Despesa com legislativo,
                               "04" #Despesa com administração do estado
)


# Chama função get_dca_mun_state
# Pode demorar vários minutos
df_dca_mun <- get_dca_mun_state( #busca informações de anexos de contas anuais para todos os municípios de um estado indicado
  year = c(2018), #ano 
  annex = "I-E", #anexo de despesa por função
  arg_cod_conta = contas_sel,#vetor previamente montado com as conta que serão usadas no filtro
  state = c(31), #estado cujos municípios serão selecionados
  In_QDCC=FALSE)

# Neste teste gerou gerou um dataframe de 7.076 linhas e 12 colunas