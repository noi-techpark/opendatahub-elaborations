-- SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
--
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- Deletes the elaborated measurements of this job from :from_ts onward, so the
-- next runs recompute them (each elaboration restarts from its newest output
-- date minus one day). Raw data and the matches ('Bluetooth match') are kept.
-- Only active stations are reset, since the job only elaborates active stations
-- (stations_bluetooth_*.sql) and would never rebuild the others.
--
-- Dry run (deletes, prints counts, rolls back):
--   psql "$JDBC" -v from_ts=2025-12-30 -f reset-elaboration.sql
-- Apply:
--   psql "$JDBC" -v from_ts=2025-12-30 -v apply=1 -f reset-elaboration.sql
--
-- Afterwards the "latest value" table (measurement) is set to the newest
-- remaining row of each series. The job's cache refresh only looks at the last
-- day, so once the job has recomputed everything run the sync again:
--   psql "$JDBC" -v sync_only=1 -v apply=1 -f reset-elaboration.sql
--
-- Run the job once the old rows are gone, repeat until the newest outputs
-- are current. Do not run while the job is running.

\set ON_ERROR_STOP on
\if :{?sync_only}
\elif :{?from_ts}
\else
  \echo 'usage: -v from_ts=YYYY-MM-DD [-v apply=1]  |  -v sync_only=1 [-v apply=1]'
  \quit
\endif

set search_path = intimev2, public;

begin;
\if :{?sync_only}
  select set_config('reset.from_ts', '9999-12-31', true) \gset
\else
  select set_config('reset.from_ts', :'from_ts', true) \gset
\endif

create temporary table reset_wanted (stationtype text, cname text, period int);
insert into reset_wanted values
  -- count_bluetooth_intime
  ('BluetoothStation', 'Bluetooth Count record',   600), ('BluetoothStation', 'Bluetooth Count record',   900),
  ('BluetoothStation', 'Bluetooth Count record',  1200), ('BluetoothStation', 'Bluetooth Count record',  1800),
  ('BluetoothStation', 'Bluetooth Count record',  3600), ('BluetoothStation', 'Bluetooth Count record', 21600),
  -- create_bluetooth_lhv
  ('BluetoothStation', 'heavy vehicle',  900), ('BluetoothStation', 'heavy vehicle',  1800), ('BluetoothStation', 'heavy vehicle', 21600),
  ('BluetoothStation', 'light vehicle',  900), ('BluetoothStation', 'light vehicle',  1800), ('BluetoothStation', 'light vehicle', 21600),
  -- count_match_intime
  ('LinkStation', 'Bluetooth Count match',  600), ('LinkStation', 'Bluetooth Count match',  900),
  ('LinkStation', 'Bluetooth Count match', 3600), ('LinkStation', 'Bluetooth Count match', 7200),
  ('LinkStation', 'Bluetooth Count match', 21600),
  -- run_mode_intime
  ('LinkStation', 'Bluetooth Elapsed time (test)',  600), ('LinkStation', 'Bluetooth Elapsed time (test)',  900),
  ('LinkStation', 'Bluetooth Elapsed time (test)', 3600),
  -- run_mode_intime_100kmh
  ('LinkStation', 'Bluetooth Elapsed time greater than 100 km/h', 600),
  -- compute_bspeed
  ('LinkStation', 'velocita''',  600), ('LinkStation', 'velocita''',  900), ('LinkStation', 'velocita''', 3600),
  -- compute_bspeed_100kmh
  ('LinkStation', 'speed greater than 100 km/h', 600);

do $$
declare missing text;
begin
  select string_agg(distinct w.cname, ', ') into missing
    from reset_wanted w left join type y on y.cname = w.cname
   where y.id is null;
  if missing is not null then
    raise exception 'unknown data types: %', missing;
  end if;
end $$;

create temporary table reset_series on commit drop as
select t.id as timeseries_id, t.partition_id, w.stationtype, w.cname as type_name, t.period
  from reset_wanted w
  join type y on y.cname = w.cname
  join station s on s.stationtype = w.stationtype and s.active
  join timeseries t on t.station_id = s.id and t.type_id = y.id and t.period = w.period
 where t.value_table = 'measurement';

alter table reset_series add column deleted bigint default 0;

-- one delete per series, so each uses the (timeseries_id, timestamp) index
-- (with sync_only the cut-off is far in the future and nothing is deleted)
do $$
declare r record; n bigint;
begin
  for r in select * from reset_series loop
    delete from measurementhistory h
     where h.timeseries_id = r.timeseries_id
       and h.partition_id = r.partition_id
       and h.timestamp >= current_setting('reset.from_ts')::timestamp;
    get diagnostics n = row_count;
    update reset_series s set deleted = n
     where s.timeseries_id = r.timeseries_id and s.partition_id = r.partition_id;
  end loop;
end $$;

-- measurement keeps the newest record per series: point it at the newest
-- remaining history row, or remove it when the series is empty
alter table reset_series add column latest text default 'unchanged';

do $$
declare r record; h record; n bigint; has_row boolean;
begin
  for r in select * from reset_series loop
    select ho.timestamp, ho.double_value into h
      from measurementhistory ho
     where ho.timeseries_id = r.timeseries_id and ho.partition_id = r.partition_id
     order by ho.timestamp desc limit 1;
    has_row := found;
    if has_row then
      update measurement m set timestamp = h.timestamp, double_value = h.double_value
       where m.timeseries_id = r.timeseries_id
         and (m.timestamp, m.double_value) is distinct from (h.timestamp, h.double_value);
      get diagnostics n = row_count;
      if n = 0 and not exists (select 1 from measurement m where m.timeseries_id = r.timeseries_id) then
        insert into measurement (created_on, timeseries_id, timestamp, double_value)
        values (current_timestamp, r.timeseries_id, h.timestamp, h.double_value);
        n = 1;
      end if;
    else
      delete from measurement m where m.timeseries_id = r.timeseries_id;
      get diagnostics n = row_count;
    end if;
    if n > 0 then
      update reset_series s set latest = case when has_row then 'set' else 'removed' end
       where s.timeseries_id = r.timeseries_id and s.partition_id = r.partition_id;
    end if;
  end loop;
end $$;

select stationtype, type_name, count(*) as timeseries, sum(deleted) as deleted,
       count(*) filter (where latest <> 'unchanged') as latest_changed
  from reset_series
 group by rollup (stationtype, type_name)
 order by stationtype, type_name;

\if :{?apply}
  commit;
  \echo 'APPLIED'
\else
  rollback;
  \echo 'DRY RUN, rolled back. Add -v apply=1 to apply.'
\endif
