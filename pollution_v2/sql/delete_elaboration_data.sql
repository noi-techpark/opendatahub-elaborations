-- SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
--
-- SPDX-License-Identifier: CC0-1.0

-- this script deletes all data (double, json and string measurements) created by the pollution v2 elaboration (emissions and validation) beginning with a starting date

set search_path=intimev2,public;

create temporary table tmp_delete as
with
vars as (select
	timestamp '2023-01-01 00:00:00' as start_date
)
select distinct ts.id as timeseries_id, ts.value_table, s.stationtype, s.origin, t.cname, v.start_date
from station s
cross join vars v
join timeseries ts on ts.station_id = s.id
join type t on t.id = ts.type_id
where s.stationtype = 'TrafficSensor'
  and s.origin = 'A22'
  and (t.cname like '%-emissions' or t.cname like '%-VALID');

-- DOUBLE

delete from measurementhistory mh
using tmp_delete b
where b.value_table = 'measurement'
and mh.timeseries_id = b.timeseries_id
and mh.timestamp > b.start_date;

-- delete the cached current-value row if no history is left to restore it from...
delete from measurement m
using tmp_delete b
where b.value_table = 'measurement'
and m.timeseries_id = b.timeseries_id
and m.timestamp > b.start_date
and not exists (select 1 from measurementhistory mh where mh.timeseries_id = m.timeseries_id);

-- ...otherwise restore it to the most recent surviving history record
update measurement m
set timestamp = h.timestamp, double_value = h.double_value, created_on = h.created_on, provenance_id = h.provenance_id
from tmp_delete b
join lateral (
	select mh.timestamp, mh.double_value, mh.created_on, mh.provenance_id
	from measurementhistory mh
	where mh.timeseries_id = b.timeseries_id
	order by mh.timestamp desc
	limit 1
) h on true
where b.value_table = 'measurement'
and m.timeseries_id = b.timeseries_id
and m.timestamp > b.start_date;

-- JSON

delete from measurementjsonhistory mh
using tmp_delete b
where b.value_table = 'measurementjson'
and mh.timeseries_id = b.timeseries_id
and mh.timestamp > b.start_date;

delete from measurementjson m
using tmp_delete b
where b.value_table = 'measurementjson'
and m.timeseries_id = b.timeseries_id
and m.timestamp > b.start_date
and not exists (select 1 from measurementjsonhistory mh where mh.timeseries_id = m.timeseries_id);

update measurementjson m
set timestamp = h.timestamp, json_value = h.json_value, created_on = h.created_on, provenance_id = h.provenance_id
from tmp_delete b
join lateral (
	select mh.timestamp, mh.json_value, mh.created_on, mh.provenance_id
	from measurementjsonhistory mh
	where mh.timeseries_id = b.timeseries_id
	order by mh.timestamp desc
	limit 1
) h on true
where b.value_table = 'measurementjson'
and m.timeseries_id = b.timeseries_id
and m.timestamp > b.start_date;

-- STRING

delete from measurementstringhistory mh
using tmp_delete b
where b.value_table = 'measurementstring'
and mh.timeseries_id = b.timeseries_id
and mh.timestamp > b.start_date;

delete from measurementstring m
using tmp_delete b
where b.value_table = 'measurementstring'
and m.timeseries_id = b.timeseries_id
and m.timestamp > b.start_date
and not exists (select 1 from measurementstringhistory mh where mh.timeseries_id = m.timeseries_id);

update measurementstring m
set timestamp = h.timestamp, string_value = h.string_value, created_on = h.created_on, provenance_id = h.provenance_id
from tmp_delete b
join lateral (
	select mh.timestamp, mh.string_value, mh.created_on, mh.provenance_id
	from measurementstringhistory mh
	where mh.timeseries_id = b.timeseries_id
	order by mh.timestamp desc
	limit 1
) h on true
where b.value_table = 'measurementstring'
and m.timeseries_id = b.timeseries_id
and m.timestamp > b.start_date;
