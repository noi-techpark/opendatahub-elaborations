-- SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
-- SPDX-License-Identifier: CC0-1.0

/* Check consistency for total and equiv data types */
select ml.timestamp, s.stationcode, p.stationcode as parent, s.stationtype, 
ml.double_value as "light", 
mh.double_value as "heavy",
mb.double_value as "bus",
mt.double_value as "total",
me.double_value as "equiv",
(ml.double_value + mh.double_value + mb.double_value) as calc_total,
(ml.double_value + mh.double_value * 2.5 + mb.double_value * 2.5) as calc_equiv
from station s
left outer join station p on p.id = s.parent_id
join type l on l.cname = 'Nr. Light Vehicles'
join timeseries tsl on tsl.type_id = l.id and tsl.station_id = s.id and tsl.period = 86400
join measurement ml on ml.timeseries_id = tsl.id
join type h on h.cname = 'Nr. Heavy Vehicles'
join timeseries tsh on tsh.type_id = h.id and tsh.station_id = s.id and tsh.period = 86400
join measurement mh on mh.timeseries_id = tsh.id and mh.timestamp = ml.timestamp
join type b on b.cname = 'Nr. Buses'
join timeseries tsb on tsb.type_id = b.id and tsb.station_id = s.id and tsb.period = 86400
join measurement mb on mb.timeseries_id = tsb.id and mb.timestamp = ml.timestamp
join type e on e.cname = 'Nr. Equivalent Vehicles'
join timeseries tse on tse.type_id = e.id and tse.station_id = s.id and tse.period = 86400
join measurement me on me.timeseries_id = tse.id and me.timestamp = ml.timestamp
join type t on t.cname = 'Nr. Vehicles'
join timeseries tst on tst.type_id = t.id and tst.station_id = s.id and tst.period = 86400
join measurement mt on mt.timeseries_id = tst.id and mt.timestamp = ml.timestamp
where s.stationcode like 'A22:%' and s.stationtype in ('TrafficDirection','TrafficSensor')
order by s.stationcode, ml.timestamp desc