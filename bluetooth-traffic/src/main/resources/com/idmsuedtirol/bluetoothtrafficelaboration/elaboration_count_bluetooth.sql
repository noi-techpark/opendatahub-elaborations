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

--
--  output_type_id = 19      # Elaboration type is 19
--  input_type_id = 15       # Bluetooth detection type_id
--

with params as
(
   select   ?::int as period,
            ?::int as station_id,
            19     as type_id  -- bluetooth count elaboration
)
,
stations_min_max as
(
   select *,
          (
          select min(timestamp)
            from measurementstringhistory h
            join timeseries ts on ts.id = h.timeseries_id and ts.partition_id = h.partition_id
           where ts.type_id = 15 -- bluetooth measure
             and ts.station_id = p.station_id
          ) min_timestamp
          ,
          (
          select max(timestamp)
            from measurementstringhistory h
            join timeseries ts on ts.id = h.timeseries_id and ts.partition_id = h.partition_id
           where ts.type_id = 15 -- bluetooth measure
             and ts.station_id = p.station_id
          ) max_timestamp,
          (
          select max(timestamp)::date - 1
            from measurementhistory h
            join timeseries ts on ts.id = h.timeseries_id and ts.partition_id = h.partition_id
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
                   elaboration_timestamp, -- TODO: 24 hours before last timestamp in elaboration history
                   '2017-01-01'::date  -- Limit new elaborations from year 2017
                   )::timestamp as start_calc
     from stations_min_max
    where min_timestamp is not null -- exclude stations with no data
)
,
series as
(
   select *,
          generate_series(start_calc, 
                          max_timestamp, 
                          period * '1 second'::interval) as time_window_start
     from calc_min_max
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
          ( select count(m.timestamp)
              from measurementstringhistory m
              join timeseries t on t.id = m.timeseries_id and t.partition_id = m.partition_id
             where t.station_id = r.station_id
               and t.type_id = 15
               and time_window_start <= m.timestamp 
               and m.timestamp < time_window_end
          ) as value,
          -1 as provenance_id,
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
