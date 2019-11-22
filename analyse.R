library(tidyverse)
library(lubridate)
library(DBI)

library(tidytext)
library(wordcloud)
library(dplyr)

pl_stop_words <- read_lines("pl_stop_words.txt")

# DB stuff
conn <- dbConnect(RSQLite::SQLite(), "twitter.sqlite")

# load tweets
tweets <- dbGetQuery(conn, "SELECT * FROM tweets") %>%
  # correct datetime
  mutate(datetime = as.POSIXct(strptime(date, "%a %b %d %H:%M:%S %z %Y") %>% with_tz("Europe/Warsaw")) - hours(2)) %>%
  as_tibble() %>%
  select(user, tweetText, datetime)

# close DB
dbDisconnect(conn)

# data table is ready
tweets

# who tweets most?
tweets %>%
  count(user, sort = TRUE) %>%
  top_n(20, n) %>%
  arrange(n) %>%
  mutate(user = fct_inorder(user)) %>%
  ggplot() +
  geom_col(aes(user, n), fill = "lightblue", color = "gray30") +
  coord_flip() +
  theme_minimal()


# word cloud
words <- tweets %>%
  unnest_tokens("word", tweetText, token = "tweets") %>%
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
  mutate(tweetText = str_replace_all(tweetText, "@\\w+|http|https|t.co", " ")) %>%
  unnest_tokens("word", tweetText, token = "ngrams", n = 2) %>%
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



# how many tweets per minute?
tweets %>%
  mutate(time = floor_date(datetime, unit = "minute")) %>%
  count(time) %>%
  ggplot() +
  geom_area(aes(time, n), fill = "lightblue", color = "gray30") +
  theme_minimal()
