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
--  output_type_id = 21      # Elaboration type
--  input_type_id  = 15      # Bluetooth detection type_id
--
--
-- Algorithm
--
-- a) the mac address is the same on both start and end stations
-- b) end timestamp is after start timestamp
-- c) end timestamp is less than one hour greater than the start timestamp
-- d) between the start and end timestamp must not exist another start or end timestamp with the same mac address
--
--
with params as
(
   select    ?::int as p_period,
             ?::int as link_station_id,
            21::int as elaboration_type_id
)
,
start_end_station as
(
   select *,
          -- subselects ensures that there is no more than one record for this link_station_id
          (
             select origin_id
               from intimev2.edge
              where edge_data_id = link_station_id
          ) origin_id,
          (
             select destination_id
               from intimev2.edge
              where edge_data_id = link_station_id
          ) destination_id
     from params
)
,
stations_min_max as
(
   select *,
          (
          select min(timestamp)
            from measurementstringhistory h
           where type_id = 15
             and h.station_id = ses.origin_id
          ) min_timestamp
          ,
          (
          select max(timestamp)
            from measurementstringhistory h
           where type_id = 15
             and h.station_id = ses.origin_id
          ) max_timestamp,
          (
          select max(timestamp)::date - 1
            from measurementhistory eh
           where eh.period = ses.p_period
             and eh.station_id = ses.link_station_id
             and eh.type_id = ses.elaboration_type_id
          ) elaboration_timestamp
          from start_end_station ses
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
start_point as 
(
	select *
	  from calc_min_max mm
	 inner join measurementstringhistory h 
	    on h.type_id = 15
	   and h.station_id = mm.origin_id
	   and mm.start_calc <= h.timestamp
	   and h.timestamp <= mm.max_timestamp
	 order by timestamp
)
,
matches as
(
   select *,
          (
              select min(timestamp)
                from measurementstringhistory finish
               where finish.type_id = 15
                 and finish.station_id = start.destination_id
                 and start.timestamp < finish.timestamp
                 and start.string_value = finish.string_value -- same mac address
                 and finish.timestamp < start.timestamp + '3600 seconds'::interval
          ) finish_timestamp,
          (
              select min(timestamp)
                from measurementstringhistory finish
               where finish.type_id = 15
                 and station_id = start.origin_id
                 and start.timestamp < finish.timestamp
                 and start.string_value = finish.string_value -- same mac address
                 and finish.timestamp < start.timestamp + '3600 seconds'::interval
          ) start2_timestamp
     from start_point start
)
,
result as
(
select null::bigint id,
       current_timestamp created_on,
       p_period,
       timestamp,
       (extract(epoch from finish_timestamp - timestamp)) as value,
       -1 as provenience_id,
       link_station_id,
       elaboration_type_id
  from matches
 where finish_timestamp is not null
   and (start2_timestamp is null or start2_timestamp > finish_timestamp)
    -- 2019-06-19 d@vide.bz: remove identical rows with group by
 group by 1,2,3,4,5,6,7,8
)
select deltart((select array_agg(result::intimev2.measurementhistory) from result where value is not null),
               start_calc,
               max_timestamp,
               link_station_id,
               elaboration_type_id,
               p_period,
               true),
       start_calc,
       max_timestamp
  from calc_min_max
