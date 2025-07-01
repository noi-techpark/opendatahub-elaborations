-- SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
--
-- SPDX-License-Identifier: CC0-1.0

-- this script deletes all data (double measurements, extend it if strings exist) created by the pollution v2 elaboration beginning with a starting date

set search_path=intimev2,public;

with 
vars as (select 
	'odh-mobility-el-pollution-v2' as provenance, 
	timestamp '2023-01-01 00:00:00' as start_date
),
base as (
select distinct s.id as station_id, s.stationtype, s.origin, t.cname, t.id as type_id, m."period", p.id as provenance_id, v.start_date
	from station s
		cross join vars v
		join measurement m on m.station_id = s.id
		join type t on t.id = m.type_id
		join provenance p on p.id  = m.provenance_id
    where p.data_collector = v.provenance)
delete from measurementhistory mh
  using base b
  where mh.station_id = b.station_id
  and mh.type_id = b.type_id
  and mh.period = b.period
  and mh.provenance_id = b.provenance_id
  and mh.timestamp > b.start_date;


with 
vars as (select 
	'odh-mobility-el-pollution-v2' as provenance, 
	timestamp '2023-01-01 00:00:00' as start_date
),
base as (
select distinct s.id as station_id, s.stationtype, s.origin, t.cname, t.id as type_id, m."period", p.id as provenance_id, v.start_date
	from station s
		cross join vars v
		join measurement m on m.station_id = s.id
		join type t on t.id = m.type_id
		join provenance p on p.id  = m.provenance_id
    where p.data_collector = v.provenance)
delete from  measurement m 
using base b
  where m.station_id = b.station_id
  and m.type_id = b.type_id
  and m.period = b.period
  and m.timestamp > b.start_date
  and (select max(timestamp) from measurementhistory mh where mh.station_id = m.station_id  and mh.type_id = m.type_id and mh.period = m.period) is null;

with 
vars as (select 
	'odh-mobility-el-pollution-v2' as provenance, 
	timestamp '2023-01-01 00:00:00' as start_date
),
base as (
select distinct s.id as station_id, s.stationtype, s.origin, t.cname, t.id as type_id, m."period", p.id as provenance_id, v.start_date
	from station s
		cross join vars v
		join measurement m on m.station_id = s.id
		join type t on t.id = m.type_id
		join provenance p on p.id  = m.provenance_id
    where p.data_collector = v.provenance)
update measurement m set timestamp = (select max(timestamp) from measurementhistory mh where mh.station_id = m.station_id  and mh.type_id = m.type_id and mh.period = m.period)
from base b
  where m.station_id = b.station_id
  and m.type_id = b.type_id
  and m.period = b.period
  and m.timestamp > b.start_date;