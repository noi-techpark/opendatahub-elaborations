-- SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
-- SPDX-License-Identifier: CC0-1.0

/* Check consistency for total and equiv data types */
select ml.timestamp, s.stationcode, s.stationtype,
ml.double_value as "light", 
mh.double_value as "heavy",
mb.double_value as "bus",
mt.double_value as "total",
me.double_value as "equiv",
(ml.double_value + mh.double_value + mb.double_value) as calc_total,
(ml.double_value + mh.double_value * 2.5 + mb.double_value * 2.5) as calc_equiv
from station s
join type l on l.cname = 'Nr. Light Vehicles'
join measurement ml on ml.type_id = l.id and ml.station_id = s.id and ml.period = 86400
join type h on h.cname = 'Nr. Heavy Vehicles'
join measurement mh on mh.type_id = h.id and mh.station_id = s.id and mh.period = 86400 and mh.timestamp = ml.timestamp
join type b on b.cname = 'Nr. Buses'
join measurement mb on mb.type_id = b.id and mb.station_id = s.id and mb.period = 86400 and mb.timestamp = ml.timestamp
join type e on e.cname = 'Nr. Equivalent Vehicles'
join measurement me on me.type_id = e.id and me.station_id = s.id and me.period = 86400 and me.timestamp = ml.timestamp
join type t on t.cname = 'Nr. Vehicles'
join measurement mt on mt.type_id = t.id and mt.station_id = s.id and mt.period = 86400 and mt.timestamp = ml.timestamp
where stationcode like 'A22:%' and stationtype in ('TrafficDirection','TrafficSensor')
order by s.stationcode, ml.timestamp desc