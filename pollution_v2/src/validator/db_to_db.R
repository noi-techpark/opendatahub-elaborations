# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

library(dplyr)
library(RSQLite)
library(lubridate)

conn <- dbConnect(RSQLite::SQLite(), "/home/nicola/lavori_local/2023_21_INF_OpenDataHub/08-software/validator/data/input/A22trafficdata.db")
query <- "SELECT * FROM A22trafficdata"
result <- dbGetQuery(conn, query)
dbDisconnect(conn)

df <- result %>%
  pivot_longer(cols = -c(datetime, spira),
               names_to = "variable",
               values_to = "value") %>%
  mutate(
    station_code = as.numeric(gsub("[^0-9]", "", variable)),
    station_code = paste0("A22:", spira, ":", station_code),
    variable = gsub("[^a-z]", "", variable)
  ) %>%
  mutate(variable = case_when(variable == 'b' ~ 'Nr. Buses',
                              variable == 'l' ~ 'Nr. Light Vehicles',
                              variable == 'p'~ 'Nr. Heavy Vehicles')) %>%
  select(time = datetime, station_code, variable, value) %>%


  mutate(time = ymd_hm(time),
         date = date(time)) %>%
  mutate(lane = sapply(strsplit(station_code, ":"), function(x) x[3])) %>%
  mutate(direction = case_when(lane == 1 | lane == 2 ~ 'NORD',
                               lane == 3 | lane == 4 ~ 'SUD'))

conn <- dbConnect(RSQLite::SQLite(), "/home/nicola/lavori_local/2023_21_INF_OpenDataHub/08-software/validator/data/input/odh.db")
dbWriteTable(conn, "ODH_raw_data", df, append = TRUE)
dbDisconnect(conn)
