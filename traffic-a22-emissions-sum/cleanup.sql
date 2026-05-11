-- SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
--
-- SPDX-License-Identifier: CC0-1.0

set search_path = intimev2;
SET work_mem = '1GB';

create temporary table tmp_timeseries as
select ts.id, ts.partition_id
from timeseries ts
join station s on s.id = ts.station_id
join type t on t.id = ts.type_id
where s.origin = 'A22'
and (cname like 'CO2-emissions%' or cname like 'NOx-emissions%');

create index on tmp_timeseries(id);

DO $$
DECLARE
    batch_size INT := 100000;
    batch_num INT;
    t_start TIMESTAMP;
    t_batch TIMESTAMP;
    rec RECORD;
    cur_offset INT;
    has_rows BOOLEAN;
BEGIN
    -- measurementhistory
    RAISE NOTICE '[%] Starting measurementhistory deletes', clock_timestamp();
    t_start := clock_timestamp();
    batch_num := 0;
    cur_offset := 0;
    LOOP
        has_rows := false;
        t_batch := clock_timestamp();

        FOR rec IN
            SELECT id, partition_id FROM tmp_timeseries ORDER BY id LIMIT batch_size OFFSET cur_offset
        LOOP
            has_rows := true;
            DELETE FROM measurementhistory mh
            WHERE mh.timeseries_id = rec.id
              AND mh.partition_id = rec.partition_id;
        END LOOP;

        EXIT WHEN NOT has_rows;
        batch_num := batch_num + 1;
        RAISE NOTICE '[%] measurementhistory batch % (offset %) in %ms',
            clock_timestamp(), batch_num, cur_offset,
            EXTRACT(MILLISECONDS FROM clock_timestamp() - t_batch)::INT;
        cur_offset := cur_offset + batch_size;
        COMMIT;
    END LOOP;
    RAISE NOTICE '[%] measurementhistory done: % batches in %',
        clock_timestamp(), batch_num, clock_timestamp() - t_start;

    -- measurementstringhistory
    RAISE NOTICE '[%] Starting measurementstringhistory deletes', clock_timestamp();
    t_start := clock_timestamp();
    batch_num := 0;
    cur_offset := 0;
    LOOP
        has_rows := false;
        t_batch := clock_timestamp();

        FOR rec IN
            SELECT id, partition_id FROM tmp_timeseries ORDER BY id LIMIT batch_size OFFSET cur_offset
        LOOP
            has_rows := true;
            DELETE FROM measurementstringhistory mh
            WHERE mh.timeseries_id = rec.id
              AND mh.partition_id = rec.partition_id;
        END LOOP;

        EXIT WHEN NOT has_rows;
        batch_num := batch_num + 1;
        RAISE NOTICE '[%] measurementstringhistory batch % (offset %) in %ms',
            clock_timestamp(), batch_num, cur_offset,
            EXTRACT(MILLISECONDS FROM clock_timestamp() - t_batch)::INT;
        cur_offset := cur_offset + batch_size;
        COMMIT;
    END LOOP;
    RAISE NOTICE '[%] measurementstringhistory done: % batches in %',
        clock_timestamp(), batch_num, clock_timestamp() - t_start;

    -- measurementjsonhistory
    RAISE NOTICE '[%] Starting measurementjsonhistory deletes', clock_timestamp();
    t_start := clock_timestamp();
    batch_num := 0;
    cur_offset := 0;
    LOOP
        has_rows := false;
        t_batch := clock_timestamp();

        FOR rec IN
            SELECT id, partition_id FROM tmp_timeseries ORDER BY id LIMIT batch_size OFFSET cur_offset
        LOOP
            has_rows := true;
            DELETE FROM measurementjsonhistory mh
            WHERE mh.timeseries_id = rec.id
              AND mh.partition_id = rec.partition_id;
        END LOOP;

        EXIT WHEN NOT has_rows;
        batch_num := batch_num + 1;
        RAISE NOTICE '[%] measurementjsonhistory batch % (offset %) in %ms',
            clock_timestamp(), batch_num, cur_offset,
            EXTRACT(MILLISECONDS FROM clock_timestamp() - t_batch)::INT;
        cur_offset := cur_offset + batch_size;
        COMMIT;
    END LOOP;
    RAISE NOTICE '[%] measurementjsonhistory done: % batches in %',
        clock_timestamp(), batch_num, clock_timestamp() - t_start;
END$$;

delete from measurement mh
using tmp_timeseries ts
where ts.id = mh.timeseries_id;

delete from measurementstring mh
using tmp_timeseries ts
where ts.id = mh.timeseries_id;

delete from measurementjson mh
using tmp_timeseries ts
where ts.id = mh.timeseries_id;

DO $$
DECLARE
  deleted INT;
BEGIN
  LOOP
    DELETE FROM timeseries ts
    USING (
      SELECT ts.id FROM tmp_timeseries ts
      LIMIT 1000
    ) batch
    WHERE ts.id = batch.id;

    GET DIAGNOSTICS deleted = ROW_COUNT;
    RAISE NOTICE 'Deleted: %', deleted;
    EXIT WHEN deleted = 0;
  END LOOP;
END $$;