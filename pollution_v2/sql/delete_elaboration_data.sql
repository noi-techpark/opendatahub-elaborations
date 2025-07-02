-- SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
--
-- SPDX-License-Identifier: CC0-1.0

-- this script deletes all data (double measurements, extend it if strings exist) created by the pollution v2 elaboration beginning with a starting date

set search_path=intimev2,public;

set search_path=intimev2,public;

create temporary table tmp_delete as
with
vars as (select
	timestamp '2023-01-01 00:00:00' as start_date
)
select distinct s.id as station_id, s.stationtype, s.origin, t.cname, t.id as type_id, m."period", v.start_date
from station s
cross join vars v
join measurement m on m.station_id = s.id
join type t on t.id = m.type_id
where s.stationtype = 'TrafficSensor'
  and s.origin = 'A22'
  and t.cname like '%-emissions'
  and t.cname not like 'testuh_staging%';

delete from measurementhistory mh
using tmp_delete b
where mh.station_id = b.station_id
and mh.type_id = b.type_id
and mh.period = b.period
and mh.timestamp > b.start_date;

-- This is faster for testing instead of the following two:

-- update measurement m set timestamp = b.start_date
-- from tmp_delete b
-- where m.station_id = b.station_id
-- and m.type_id = b.type_id
-- and m.period = b.period
-- and m.timestamp > b.start_date;

delete from  measurement m
using tmp_delete b
where m.station_id = b.station_id
and m.type_id = b.type_id
and m.period = b.period
and m.timestamp > b.start_date
and (select max(timestamp) from measurementhistory mh where mh.station_id = m.station_id  and mh.type_id = m.type_id and mh.period = m.period) is null;

update measurement m set timestamp = (select max(timestamp) from measurementhistory mh where mh.station_id = m.station_id  and mh.type_id = m.type_id and mh.period = m.period)
from tmp_delete b
where m.station_id = b.station_id
and m.type_id = b.type_id
and m.period = b.period
and m.timestamp > b.start_date;
