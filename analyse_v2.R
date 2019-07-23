library(tidyverse)
library(lubridate)
library(DBI)


library(tidytext)
library(wordcloud)

library(igraph)


pl_stop_words <- read_lines("pl_stop_words.txt")


# DB stuff
conn <- dbConnect(RSQLite::SQLite(), "twitter2.sqlite")

# load tweets
tweets <- dbGetQuery(conn, "SELECT * FROM tweets") %>%
  as_tibble() %>%
  mutate(datetime = as.POSIXct(as.numeric(timestamp)/1000, origin = "1970-01-01"))

# close DB
dbDisconnect(conn)


# data table is ready
summary(tweets)



# who tweets most?
tweets %>%
  mutate(answer_tweet = in_reply_to_user_id != "None") %>%
  count(user_screen_name, answer_tweet, sort = TRUE) %>%
  group_by(user_screen_name) %>%
  mutate(nn = sum(n)) %>%
  ungroup() %>%
  top_n(40, nn) %>%
  arrange(nn) %>%
  mutate(user_screen_name = fct_inorder(user_screen_name)) %>%
  ggplot() +
  geom_col(aes(user_screen_name, y = if_else(answer_tweet, n, -n),
               fill = answer_tweet),  color = "gray30") +
  coord_flip() +
  theme_minimal()



# word cloud
words <- tweets %>%
  unnest_tokens("word", message, token = "tweets") %>%
  count(word, sort = TRUE) %>%
  filter(!word %in% pl_stop_words) %>%
  filter(str_sub(word, 1, 1) != "@") %>%
  filter(str_sub(word, 1, 4) != "http")

words_f <- words %>% filter(n > 1)

wordcloud(words_f$word, words_f$n,
          max.words = 100,
          scale = c(1.8, 0.6),
          colors = RColorBrewer::brewer.pal(9, "OrRd")[4:5])



# word cloud - bigrams
biwords <- tweets %>%
  mutate(message = str_replace_all(message, "@\\w+", " ")) %>%
  mutate(message = str_replace_all(message, "(www|http:|https:)+[^\\s]+[\\w]", " ")) %>%
  unnest_tokens("word", message, token = "ngrams", n = 2) %>%
  count(word, sort = TRUE) %>%
  filter(!is.na(word)) %>%
  separate(word, into = c("word1", "word2")) %>%
  filter(!word1 %in% pl_stop_words, !word2 %in% pl_stop_words) %>%
  filter(str_length(word1) > 2 | str_length(word2) > 2) %>%
  unite("word", c("word1", "word2"), sep = " ")



biwords_f <- biwords %>% filter(n > 1)

wordcloud(biwords_f$word, biwords_f$n,
          max.words = 100,
          scale = c(1.8, 0.6),
          colors = RColorBrewer::brewer.pal(9, "OrRd")[4:5])



# how many tweets per 5 minutee?
tweets %>%
  mutate(time = floor_date(datetime, unit = "5 minutes")) %>%
  count(time) %>%
  ggplot() +
  geom_point(aes(time, n), color = "gray30") +
  theme_minimal() +
  labs(title = "Produkcja tweetów przez osoby z listy \"dziennikarze\" od @dziennikarz",
       subtitle = "Bez RT", caption = "@lemur78, fb.com/DaneAnalizy",
       x = "", y = "Liczba tweetów na 5 minut")



# who tweets whom?
users_graph <- tweets %>%
  filter(in_reply_to_user_id != "None", user_id != in_reply_to_user_id) %>%
  count(user_id, in_reply_to_user_id, sort = TRUE) %>%
  filter(n > 1) %>%
  set_names(c("from", "to", "weight")) %>%
  graph_from_data_frame()

wc_up <- cluster_walktrap(users_graph, weights = E(users_graph)$weight)

V(users_graph)$membership <- wc_up$membership

plot(users_graph,
     vertex.size = 5,
     vertex.label.cex = 0.5,
     vertex.color = V(users_graph)$membership,
     egde.width = 5*E(users_graph)$weight,
     edge.arrow.size = 0.1,
     edge.arrow.width = 0.1)

