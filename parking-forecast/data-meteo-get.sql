-- https://weather.provinz.bz.it/south-tyrol-weather.asp
-- https://weather.provinz.bz.it/services.asp
--
-- Publication times
--
-- Our weather forecasts appear 365 days a year.
-- The report of South Tyrol is updated at 7:30 and 11:00 on working day (Mon-Sat)
-- and at 10:00 on Sundays and public holidays. The district weather forecasts appear
-- daily at 09:00.
--
-- in the DWH we store the "type": "WEAT11" forecast from 10:00 or 11:00
-- from JSON http://daten.buergernetz.bz.it/services/weather/bulletin?format=json&lang=de

-- note about stations:
-- index 2 = BZ (on map left to right)
-- codes: http://daten.buergernetz.bz.it/dataset/southtyrolean-weatherservice-weathersouthtyrol/resource/f93085b4-fece-436e-a9e2-fa4ae626a2ff

-- actual query to produce CSV with the forecast symbols a-z mapped to 0-25 starting from 2022-01-01

create temporary table meteo as
select tomorrow_date, ascii(sym) - ascii('a') as symbol_value
from (
         select (raw_json -> 'tomorrow' ->> 'date')::date as tomorrow_date,
                 raw_json -> 'tomorrow' -> 'stationData' -> 2 -> 'symbol' ->> 'code' as sym
         from weather_data.predictions_raw
     ) as sub
where tomorrow_date >= '2022-01-01'::date order by tomorrow_date;
\copy meteo to 'data-meteo/meteo.csv' with csv header
