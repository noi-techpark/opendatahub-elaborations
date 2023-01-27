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

with bluetoot_types as
(
   select unnest(ARRAY[
       19, -- 1800/21600/900 COUNT BLUETOOTH
       13, -- 1800/21600/900 COUNT BLUETOOTH HEAVY VEHICLES
       14, -- 1800/21600/900 COUNT BLUETOOTH LIGHT VEHICLES
       --
       21, -- 1              CREATE MATCHES
       20, --                COUNT  MATCHES
       918, --               MODE
       54, --                 SPEED
       --
       5968, --              MODE 100 km/h
       5969  --              SPEED 100 km/h
   ]) as b_type_id
)
,
old_values as
(
   select station_id, type_id, period,
          timestamp, double_value
     from measurement
     join bluetoot_types
       on measurement.type_id = bluetoot_types.b_type_id
)
,
pre_new_values as
(
   select *,
       row_number() over (partition by station_id, type_id, period order by timestamp desc, double_value) rownr
  from measurementhistory
  -- optimization to enable index usage
  where type_id in (19, 13, 14, 21, 20, 918, 54, 5968, 5969)
   and timestamp >= now()::date - '1 day'::interval -- search last values between now and the day before only
)
,
new_values as
(
   select *
     from pre_new_values
    where rownr = 1
)
,
diff as
(
   select coalesce(new_values.station_id, old_values.station_id) station_id,
          coalesce(new_values.type_id, old_values.type_id) type_id,
          coalesce(new_values.period, old_values.period) period,
          old_values.timestamp as old_timestamp,
          old_values.double_value as old_value,
          new_values.timestamp as new_timestamp,
          new_values.double_value as new_value
     from new_values
     full outer join old_values
       on new_values.station_id = old_values.station_id
      and new_values.type_id    = old_values.type_id
      and new_values.period     = old_values.period
    order by 1,2,3
)
,
upd as (
   update measurement e
      set timestamp = s.new_timestamp,
          double_value = s.new_value
     from (select * 
             from diff 
            where old_timestamp is not null
              and new_timestamp is not null
              and (old_timestamp != new_timestamp or old_value is distinct from new_value) -- values can be null
          ) s
    where e.station_id = s.station_id
      and e.type_id = s.type_id
      and e.period = s.period
   returning *
)
,
ins as (
   insert into measurement(created_on, station_id, type_id, period, timestamp, double_value)
   select current_timestamp, station_id, type_id, period, new_timestamp as timestamp, new_value
     from diff
    where old_timestamp is null
   returning *
)
select (select count(*) from ins) nr_insert,
       (select count(*) from upd) nr_update
