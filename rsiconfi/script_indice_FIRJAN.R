# Fernando A Barbalho
# @barbalhofernand 

# install.packages("devtools")
#devtools::install_github("tchiluanda/rsiconfi")

library(rsiconfi)
library(dplyr)
library(tidyr)

###########Trabalhando as despesas

#Monta um vetor com todos os códigos de UFs do Brasil
#Vide https://atendimento.tecnospeed.com.br/hc/pt-br/articles/360021494734-Tabela-de-C%C3%B3digo-de-UF-do-IBGE

todos_estados<-28 #para efeito de teste considera-se aqui apenas o estado de Rondônia
#todos_estados<-c(11:17,21:29,31:35,41:43,50:53) #para execução completa tire o comentário dessa linha


#Monta um vetor com as contas que se referem às despesas com a burocracia nos municípios
#para saber as contas disponíveis use a função get_account_dca, como indicado abaixo
# df_conta_dca<- get_account_dca(2018, "I-E", c("2312908") )

df_conta_dca <- get_account_dca(2018, "I-E", c("2312908") )

contas_depesas_burocaracia<- c("01", #Despesa com legislativo,
                               "04" #Despesa com administração do estado
)




#chama função que traz dados contábeis anuais de todos os municípios de um conjunto de estados
#Atenção, a execução da linha abaixo pode demorar várias horas para execução.
#Caso queira fazer somente um teste sugerimos substituir o vetor de estados.
#Considere usar apenas o estado 11-Rondônia para testes
df_desp_mun<- get_dca_mun_state(year= 2018, #ano a que se refere os dados. poderia ser um vetor de anos
                                annex= "I-E", #Anexo de Contas Anuais que se refere a despesa por função
                                state = todos_estados, #Informa o conjunto de UFs a que se refere os dados recuperados. nesse caso todos as UFs
                                arg_cod_conta = contas_depesas_burocaracia#Contas associadas a despesa com burocracia
)

#O vetor df_rec_mun apresenta várias linhas para o mesma chave composta de cod_ibge e conta.
#Deve-se escolher a fase da despesa para não haver distorção nos dados.
#Para esse caso vamos filtar as despesas liquidadas, presentes na variável coluna
#Aproveitamos para usar no dataset apenas as variáveis cod_ibge, conta e valor

df_desp_mun<- df_desp_mun %>%
  filter(coluna== "Despesas Liquidadas") %>%
  select(cod_ibge, conta, valor)

#Transpõe  a matriz de despesa para os tipos de despesa virarem coluna
df_desp_mun_tidy <- df_desp_mun %>%
  spread(conta,valor)

names(df_desp_mun_tidy)[2:3]<- c("desp_legislativa","desp_administracao")

###########Trabalhando as receitas

#Monta um vetor com as contas que se referem às receitas que são consideradas no cálculo
#para saber as contas disponíveis use a função get_account_dca, como indicado abaixo
# df_conta_dca<- get_account_dca(2018, "I-C", c("2312908") )

contas_receita<- c("1.0.0.0.00.0.0", #Receitas Correntes ,
                   "1.7.0.0.00.0.0", #Transferências correntes,
                   "RO1.7.2.8.01.1.0", #Cota-parte do ICMS,
                   "RO1.7.2.8.01.2.0", #Cota-parte do IPVA,
                   "RO1.7.1.8.01.5.0", #Cota-parte do ITR,
                   "1.7.2.8.01.3.0 Cota-Parte do IPI"#Cota-parte do IPI
)

df_rec_mun<- get_dca_mun_state(year= 2018, #ano a que se refere os dados. poderia ser um vetor de anos
                               annex= "I-C", #Anexo de Contas Anuais que se refere a receita orçamentária
                               state = todos_estados, #Informa o conjunto de UFs a que se refere os dados recuperados. nesse caso todas as UFs
                               arg_cod_conta = contas_receita#Contas associadas a receitas econômicas municipais
)


#para todas as receitas devem ser excluídas as deduções relativas a FUNDEB, transferências constitucionais e outras deduções da receita da receita bruta realizada.
#Para tanto, deve-se trabalhar com as informações que estão na variável "coluna"


df_rec_liq<- df_rec_mun %>%
  mutate(valor = ifelse(coluna== "Receitas Brutas Realizadas", valor, -valor)) %>% #Se não for Receita Bruta realizada, trata-se de dedução, o valor deve ser multipliado por -1
  group_by(cod_ibge, cod_conta) %>%
  summarise(
    valor_liquido = sum(valor)
  ) %>%
  spread(cod_conta, valor_liquido) %>%
  ungroup() %>%
  mutate(rec_econ = RO1.0.0.0.00.0.0 - RO1.7.0.0.00.0.0 + rowSums(.[4:7])) %>%
  select(1,2,8)


names(df_rec_liq)[2:3]<-c("receitas_correntes_liq", "receita_economica_mun")


####Trabalha em conjunto as informações de receita e despesa e calcula o índice FIRJAN de autonomia



df_resultado<-df_desp_mun_tidy %>%
  inner_join(df_rec_liq) %>%
  mutate(indicador = (receita_economica_mun-
                        desp_legislativa-
                        desp_administracao)/
           receitas_correntes_liq,
         IFGF_autonomia =  case_when(
           indicador > 0.25 ~ 1,
           indicador < 0.25 & indicador >0 ~ indicador/0.25,
           TRUE ~ 0))
