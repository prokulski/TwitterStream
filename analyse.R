library(tidyverse)
library(DBI)

conn <- dbConnect(RSQLite::SQLite(), "twitter.db")

dbListTables(conn)

tweets <- dbGetQuery(conn, "SELECT * FROM tweets")

tweets
