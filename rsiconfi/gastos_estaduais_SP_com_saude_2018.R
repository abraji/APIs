# -*- coding: utf-8
# Abraji (https://www.abraji.org.br)
# Reinaldo Chaves (reinaldo@abraji.org.br)
# Script exemplo de uso do rsiconfi
# Baixa gastos com saúde do Estado de SP
#

#install.packages("devtools")
#devtools::install_github("tchiluanda/rsiconfi")

library(rsiconfi)
library(dplyr)
library(tidyr)

# Códigos de UFs do Brasil
# https://atendimento.tecnospeed.com.br/hc/pt-br/articles/360021494734-Tabela-de-C%C3%B3digo-de-UF-do-IBGE
# São Paulo é 35 - entity

# Vamos ver Despesas por Função (I-E)
# A função get_account_dca retorna os códigos possíveis
# Coloco o ano 2018, o I-E e um código relacionado com SP
# Aqui a lista de todos:
# https://siconfi.tesouro.gov.br/siconfi/pages/public/conteudo/conteudo.jsf?id=581 clique em Tabela dos códigos de instituição utilizados no Siconfi - Código das Instituições

df_conta_dca <- get_account_dca(2018, "I-E", c("35") )


## Captura gastos de SP com Saúde (11)
gasto_uf_sp_2019 <- get_dca(year = 2018,
        annex = "I-E",
        entity = "35", 
        arg_cod_conta = "10")

# Os dados de 2019 ainda não estão na API


# Com um vetor dos anos posso baixar tudo e comparar depois
gasto_uf_sp <- get_dca(year = c(2013, 2014, 2015, 2016, 2017, 2018),
                            annex = "I-E",
                            entity = "35", 
                            arg_cod_conta = "10")


