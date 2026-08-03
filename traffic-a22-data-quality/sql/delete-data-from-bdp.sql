set search_path=intimev2,public;

create temporary table tmp_delete as
with
vars as (select
	timestamp '2024-07-10 00:00:00' as start_date
)
select distinct ts.id as timeseries_id, s.stationtype, s.origin, t.cname, v.start_date
from station s
cross join vars v
join timeseries ts on ts.station_id = s.id
join type t on t.id = ts.type_id
where s.stationtype in ('TrafficSensor', 'TrafficDirection')
  and s.origin = 'A22'
  and s.available = true
  and ts.period = 86400
  and t.cname in (
    'Nr. Light Vehicles',
    'Nr. Heavy Vehicles',
    'Nr. Buses',
    'Nr. Equivalent Vehicles',
    'Average Speed Light Vehicles',
    'Average Speed Heavy Vehicles',
    'Average Speed Buses',
    'Variance Speed Light Vehicles',
    'Variance Speed Heavy Vehicles',
    'Variance Speed Buses',
    'Average Gap',
    'Average Headway',
    'Average Density',
    'Average Flow'
  );

-- preview before deleting
select count(*) as timeseries_matched from tmp_delete;

delete from measurementhistory mh
using tmp_delete b
where mh.timeseries_id = b.timeseries_id
and mh.timestamp > b.start_date;

-- delete the cached current-value row if no history is left to restore it from...
delete from measurement m
using tmp_delete b
where m.timeseries_id = b.timeseries_id
and m.timestamp > b.start_date
and not exists (select 1 from measurementhistory mh where mh.timeseries_id = m.timeseries_id);

-- ...otherwise restore it to the most recent surviving history record
update measurement m
set timestamp = h.timestamp, double_value = h.double_value
from tmp_delete b
join lateral (
	select mh.timestamp, mh.double_value
	from measurementhistory mh
	where mh.timeseries_id = b.timeseries_id
	order by mh.timestamp desc
	limit 1
) h on true
where m.timeseries_id = b.timeseries_id
and m.timestamp > b.start_date;

-- verify what's left for the targeted timeseries
select m.*, t.cname, s.stationcode
from station s
join timeseries ts on ts.station_id = s.id
join measurement m on m.timeseries_id = ts.id
join type t on t.id = ts.type_id
where ts.id in (select timeseries_id from tmp_delete)
order by m.timestamp desc
limit 1000;
