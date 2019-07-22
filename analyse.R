library(tidyverse)
library(lubridate)
library(DBI)

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
