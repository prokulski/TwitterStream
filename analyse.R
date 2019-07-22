library(tidyverse)
library(lubridate)
library(DBI)


library(tidytext)
library(wordcloud)

pl_stop_words <- read_lines("pl_stop_words.txt")

# DB stuff
conn <- dbConnect(RSQLite::SQLite(), "twitter.db")

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
  count(user, sort = TRUE)


# word cloud
words <- tweets %>%
  unnest_tokens("word", tweetText, token = "tweets") %>%
  count(word, sort = TRUE) %>%
  filter(!word %in% pl_stop_words) %>%
  filter(str_sub(word, 1, 1) != "@") %>%
  filter(str_sub(word, 1, 4) != "http")

words_f <- words %>% filter(n > 1)

wordcloud(words_f$word, words_f$n,
          max.words = 200,
          scale = c(1.8, 0.6),
          colors = rev(RColorBrewer::brewer.pal(9, "OrRd")[4:5]))



# how many tweets per minute?
tweets %>%
  mutate(time = floor_date(datetime, unit = "minute")) %>%
  count(time) %>%
  ggplot() +
  geom_area(aes(time, n), fill = "lightblue", color = "gray30") +
  theme_minimal()
