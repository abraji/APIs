# -*- coding: utf-8
# Sharon Machlis (@sharon000)
# Tutorial para investigar tweets com rtweet e R
# https://www.infoworld.com/article/3515712/how-to-search-twitter-with-rtweet-and-r.html
# (Texto adaptado por Reinaldo Chaves)

# Se você precisar instalar qualquer um destes, desmarque
# install.packages("rtweet")
# install.packages("reactable")
# install.packages("glue")
# install.packages("stringr")
# install.packages("httpuv")
# install.packages("dplyr")
# install.packages("purrr")

library(rtweet)
library(dplyr)
library(readr)

## Seta diretórios
# Mostra o atual
getwd()
# Escolha o da sua preferência no seu computador
setwd("/home/reinaldo/Documentos/Code/abraji")


## Armazenar chaves da API do Twitter (esses são valores de exemplo estão em branco; substitua por suas próprias chaves)
## ATENÇÃO: TOME CUIDADO COM SUAS CHAVES DO TWITTER, NÃO MOSTRE PARA NINGUÉM!
api_key <- ""
api_secret_key <- ""
access_token <- ""
access_token_secret <- ""

## Autenticar via web browser
token <- create_token(
  app = "o nome do seu app",
  consumer_key = api_key,
  consumer_secret = api_secret_key,
  access_token = access_token,
  access_secret = access_token_secret)

## Checar se o token foi carregado
## Ou para carregar direto nas próximas vezes, sem precisar pegar as chaves de novo
get_token()

## Exempo de uma busca básica pela hashtag #rstudioconf
tweet_df <- search_tweets("#rstudioconf", n = 200, 
                          include_rts = FALSE)

## Exempo de uma busca básica pela hashtag #jornalismo
tweet_df_jorn <- search_tweets("#jornalismo", n = 200, 
                          include_rts = FALSE)
## Você pode salvar em CSV para usar depois - boa prática!
save_as_csv(tweet_df_jorn, "tweets_jorn_09_03_2020", prepend_ids = FALSE, na = "",
            fileEncoding = "UTF-8")

# Seleciona apenas algumas colunas do dataframe tweet_df
tweet_table_data <- select(tweet_df, -user_id, -status_id)

library(reactable)

# Chama o reactable para o dataframe selecionado
reactable(tweet_table_data)

# Customiza a visualização 
reactable(tweet_table_data, 
          filterable = TRUE, searchable = TRUE, bordered = TRUE, 
          striped = TRUE, highlight = TRUE,
          defaultPageSize = 25, showPageSizeOptions = TRUE, 
          showSortable = TRUE, pageSizeOptions = c(25, 50, 75, 100, 200), defaultSortOrder = "desc",
          columns = list(
            created_at = colDef(defaultSortOrder = "asc"),
            screen_name = colDef(defaultSortOrder = "asc"),
            text = colDef(html = TRUE, minWidth = 190, resizable = TRUE),
            favorite_count = colDef(filterable = FALSE),
            retweet_count = colDef(filterable =  FALSE),
            urls_expanded_url = colDef(html = TRUE)
          )
) 

# Cria novo dataframe com a URL
tweet_table_data <- tweet_df %>%
  select(user_id, status_id, created_at, screen_name, text, favorite_count, retweet_count, urls_expanded_url) %>%
  mutate(
    Tweet = glue::glue("{text} <a href='https://twitter.com/{screen_name}/status/{status_id}'>>> </a>") 
  )%>%
  select(DateTime = created_at, User = screen_name, Tweet, Likes = favorite_count, RTs = retweet_count, URLs = urls_expanded_url)


library(glue)

# Criação uma função para transformar as URL em objeto clicável
make_url_html <- function(url) {
  if(length(url) < 2) {
    if(!is.na(url)) {
      as.character(glue("<a title = {url} target = '_new' href = '{url}'>{url}</a>") )
    } else {
      ""
    }
  } else {
    paste0(purrr::map_chr(url, ~ paste0("<a title = '", .x, "' target = '_new' href = '", .x, "'>", .x, "</a>", collapse = ", ")), collapse = ", ")
  }
}
# Aciona a função make_url_html
tweet_table_data$URLs <- purrr::map_chr(tweet_table_data$URLs, make_url_html)


# Refaz o reactable agora com o dataframe já alterado
reactable(tweet_table_data, 
          filterable = TRUE, searchable = TRUE, bordered = TRUE, striped = TRUE, highlight = TRUE,
          showSortable = TRUE, defaultSortOrder = "desc", defaultPageSize = 25, showPageSizeOptions = TRUE, pageSizeOptions = c(25, 50, 75, 100, 200), 
          columns = list(
            DateTime = colDef(defaultSortOrder = "asc"),
            User = colDef(defaultSortOrder = "asc"),
            Tweet = colDef(html = TRUE, minWidth = 190, resizable = TRUE),
            Likes = colDef(filterable = FALSE, format = colFormat(separators = TRUE)),
            RTs = colDef(filterable =  FALSE, format = colFormat(separators = TRUE)),
            URLs = colDef(html = TRUE)
          )
) 



### Faz o mesmo para o dataframe tweet_df_jorn
tweet_table_data_jorn <- tweet_df_jorn %>%
  select(user_id, status_id, created_at, screen_name, text, favorite_count, retweet_count, urls_expanded_url) %>%
  mutate(
    Tweet = glue::glue("{text} <a href='https://twitter.com/{screen_name}/status/{status_id}'>>> </a>") 
  )%>%
  select(DateTime = created_at, User = screen_name, Tweet, Likes = favorite_count, RTs = retweet_count, URLs = urls_expanded_url)

tweet_table_data_jorn$URLs <- purrr::map_chr(tweet_table_data_jorn$URLs, make_url_html)

reactable(tweet_table_data_jorn, 
          filterable = TRUE, searchable = TRUE, bordered = TRUE, striped = TRUE, highlight = TRUE,
          showSortable = TRUE, defaultSortOrder = "desc", defaultPageSize = 25, showPageSizeOptions = TRUE, pageSizeOptions = c(25, 50, 75, 100, 200), 
          columns = list(
            DateTime = colDef(defaultSortOrder = "asc"),
            User = colDef(defaultSortOrder = "asc"),
            Tweet = colDef(html = TRUE, minWidth = 190, resizable = TRUE),
            Likes = colDef(filterable = FALSE, format = colFormat(separators = TRUE)),
            RTs = colDef(filterable =  FALSE, format = colFormat(separators = TRUE)),
            URLs = colDef(html = TRUE)
          )
) 
