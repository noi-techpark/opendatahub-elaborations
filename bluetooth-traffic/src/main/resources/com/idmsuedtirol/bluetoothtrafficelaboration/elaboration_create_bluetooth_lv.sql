-- SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
--
-- SPDX-License-Identifier: AGPL-3.0-or-later

/*

BluetoothTrafficElaboration: various elaborations of traffic data

Copyright (C) 2017 IDM Südtirol - Alto Adige - Italy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/
-- Davide Montesin <d@vide.bz>

with params as
(
   select   ?::int as period,
            ?::int as station_id,
            14::int as type_id
)
,
min_max as
(
   select p.period,
          p.station_id,
          p.type_id,
          -- 2019-06-19 d@vide.bz: if info is missing, then use 0% for heavy vehicles
          coalesce((
             select AVG((m.json->>'factor')::decimal * (m.json->>'hv_perc')::decimal )
			   from intimev2.edge e
			   join intimev2.station s 
			     on e.edge_data_id = s.id
			   join intimev2.metadata m 
			     on s.meta_data_id = m.id
			  where s.stationtype = 'TrafficStreetFactor'
			    and e.destination_id = p.station_id
          ),0) heavy_perc,
          (select min(timestamp)
            from measurementhistory eh
            join timeseries ts on ts.id = eh.timeseries_id and eh.partition_id = ts.partition_id
           where ts.period = p.period
             and ts.station_id = p.station_id
             and ts.type_id = 19
          ) min_timestamp, 
          (select max(timestamp)
            from measurementhistory eh
            join timeseries ts on ts.id = eh.timeseries_id and eh.partition_id = ts.partition_id
           where ts.period = p.period
             and ts.station_id = p.station_id
             and ts.type_id = 19
          ) max_timestamp,
          (
          select max(timestamp)::date - 1
            from measurementhistory eh
            join timeseries ts on ts.id = eh.timeseries_id and eh.partition_id = ts.partition_id
           where ts.period = p.period
             and ts.station_id = p.station_id
             and ts.type_id = p.type_id
          ) elaboration_timestamp
     from params p
)
,
calc_min_max as
(
   select *,
          GREATEST(min_timestamp::date, 
                   elaboration_timestamp,
                   '2017-01-01'::date
                   )::timestamp as start_calc
     from min_max
    where min_timestamp is not null
)
,
series as
(
   select *,
          generate_series(start_calc, 
                          max_timestamp, 
                          period * '1 second'::interval) as time_window_start
     from calc_min_max
    where heavy_perc is not null
)
,
range as
(
   select *, 
          time_window_start + period * '1 second'::interval as time_window_end,
          time_window_start + period / 2 * '1 second'::interval as time_window_center
     from series
)
,
result as
(
   select null::bigint id,
          current_timestamp created_on,
          period,
          time_window_center as timestamp,
          ( select double_value - floor(double_value * heavy_perc / 100)
              from measurementhistory m
              join timeseries ts on ts.id = m.timeseries_id and m.partition_id = ts.partition_id
             where ts.station_id = r.station_id
               and ts.period = r.period
               and ts.type_id = 19
               and m.timestamp = r.time_window_center
          ) as value,
          -1 as provenience_id,
          station_id,
          type_id
     from range r
)
select deltart((select array_agg(result::deltart_input) from result where value is not null),
               start_calc    + period/2 * '1 second'::interval,
               max_timestamp + period/2 * '1 second'::interval,
               station_id,
               type_id,
               period),
       start_calc    + period/2 * '1 second'::interval,
       max_timestamp + period/2 * '1 second'::interval
  from calc_min_max
