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
--  input_type_id  =  21
--  output_type_id = 918     # Elaboration type
--

--
-- take the matches within each range
-- take the min and the max value of percorrenza within each range
-- loop from min to max value of percorrenza with 5 seconds step
-- for each step count the number of values between step and step + 30 seconds
-- as mode for the range take the step with greater count and when more have the same value then the lower value


with params as
(
   select   ?::int as period,
            ?::int as station_id,
            21::int as input_type_id,
           918::int as output_type_id
)
,
min_max as
(
   select p.period,
          p.station_id,
          p.output_type_id,
          p.input_type_id,
          (select min(timestamp)
            from measurementhistory eh
           where eh.period = 1
             and eh.station_id = p.station_id
             and eh.type_id = p.input_type_id
          ) min_timestamp, 
          (select max(timestamp)
            from measurementhistory eh
           where eh.period = 1
             and eh.station_id = p.station_id
             and eh.type_id = p.input_type_id
          ) max_timestamp,
          (
          select max(timestamp)::date - 1
            from measurementhistory eh
           where eh.period = p.period
             and eh.station_id = p.station_id
             and eh.type_id = p.output_type_id
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
)
,
range as
(
   select *, 
          time_window_start + period * '1 second'::interval as time_window_end,
          time_window_start + period / 2 * '1 second'::interval as time_window_center
     from series
    order by time_window_start
    limit 4000 -- truncate too much long elaborations. must be longer than 2 days.
)
,
samples as
(
select *
  from range
  join measurementhistory eh
    on eh.type_id = input_type_id
   and eh.station_id = range.station_id
   and eh.period = 1
   and time_window_start <= eh.timestamp
   and eh.timestamp < time_window_end
 where eh.timestamp >= '2017-01-01'::date
)
,
min_max_value as
(
   select *,
          floor((select min(double_value)
             from samples
            where samples.time_window_start = range.time_window_start
          )) min_value,
          ceil((select max(double_value)
             from samples
            where samples.time_window_start = range.time_window_start
          )) max_value,
          (select count(*)
             from samples
            where samples.time_window_start = range.time_window_start
          ) as values_count
     from range
)
,
min_max_value_series as
(
select *,
       generate_series(min_value::int, max_value::int, 5) as value_step
  from min_max_value
)
,
min_max_value_series_count as
(
select m.time_window_start, m.value_step, count(s.id)
  from min_max_value_series m
  left outer join samples s on s.time_window_start = m.time_window_start
     and m.value_step <= s.double_value
     and s.double_value < m.value_step + 30
  group by m.time_window_start, m.value_step
),
,
min_max_value_max_count as (
select *,
       (select max(count)
          from min_max_value_series_count
         where min_max_value_series_count.time_window_start = min_max_value.time_window_start) max_count
  from min_max_value
)
,
mode as (
select *,
       (
          select min(value_step)
            from min_max_value_series_count
           where min_max_value_series_count.time_window_start = min_max_value_max_count.time_window_start
             and min_max_value_series_count.count = min_max_value_max_count.max_count
       )
       as mode_value
  from min_max_value_max_count
)
,
result as (
select null::bigint id,
       current_timestamp created_on,
       period,
       time_window_center as timestamp,
       -- 2019-06-19 d@vide.bz: value can't anymore be null, using coalesce(x, -1) if mode is not calcolable
       -- 2020-02-19 d@vide.bz: removed coalesce because the "from result where value is not null"
       mode_value + 15 as value, -- use center  
       -1 as provenience_id,
       station_id,
       output_type_id as type_id
  from mode
)
select deltart((select array_agg(result::intimev2.measurementhistory) from result where value is not null),
               start_calc    + period/2 * '1 second'::interval,
               max_timestamp + period/2 * '1 second'::interval,
               station_id,
               output_type_id,
               period),
       start_calc    + period/2 * '1 second'::interval,
       max_timestamp + period/2 * '1 second'::interval
  from calc_min_max
