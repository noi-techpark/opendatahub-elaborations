-- SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
--
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- -----------------------------------------------------------------------------------
--
-- intimev2.deltart()
-- function to perform a DELete/upDAte/inseRT into the measurementhistory table
--
-- Note that the schema for table measurementhistory is NOT explicitly given,
-- so a session that uses this function needs to have the correct search_path, e.g.
--
--     set search_path = intimev2, public;
--
-- -----------------------------------------------------------------------------------

-- Create a type that matches the old measurementhistory structure for compatibility
drop type if exists intimev2.deltart_input cascade;
create type intimev2.deltart_input as (
    id bigint,
    created_on timestamp,
    period integer,
    timestamp timestamp,
    double_value double precision,
    provenance_id bigint,
    station_id bigint,
    type_id bigint
);

drop function if exists intimev2.deltart;
create function intimev2.deltart
(
    p_arr         intimev2.deltart_input[],
    p_mints       timestamp without time zone,
    p_maxts       timestamp without time zone,
    p_station_id  bigint,
    p_type_id     bigint,
    p_period      bigint,
    p_extkey      boolean            default false,
    p_epsilon     double precision   default 0.0
)
returns
    int[]
as
$$
    declare
        ele intimev2.deltart_input;
        rec record;
        val double precision;
        cnt bigint;
        ret int[4];
        v_timeseries_id int4;
        v_partition_id int2;
    begin
        ret[1] := 0;  -- DELete count
        ret[2] := 0;  -- upDAte count
        ret[3] := 0;  -- inseRT count
        ret[4] := coalesce(array_length(p_arr, 1),0); -- input element count

        -- Check if timeseries record exists
        select id, partition_id into v_timeseries_id, v_partition_id
        from intimev2.timeseries 
        where station_id = p_station_id 
          and type_id = p_type_id 
          and period = p_period
          and value_table = 'measurement';


        create temporary table tt (
            timestamp    timestamp without time zone,
            double_value double precision,
            station_id   bigint,
            type_id      bigint,
            period       integer
        );

        if (array_length(p_arr, 1) > 0) then
            -- Create missing timeseries record if we have data to insert
            if (v_timeseries_id is null) then
                insert into intimev2.timeseries (station_id, type_id, period, value_table, partition_id)
                values (p_station_id, p_type_id, p_period, 'measurement', 1)
                returning id, partition_id into v_timeseries_id, v_partition_id;
            end if;
            -- loop over array for insert and copy the array into a temporary table
            foreach ele in array p_arr loop
                insert into tt
                    (timestamp, double_value, station_id, type_id, period)
                    values (ele.timestamp, ele.double_value, ele.station_id, ele.type_id, ele.period);

                if (ele.station_id != p_station_id or ele.type_id != p_type_id or ele.period != p_period) then
                    drop table tt;
                    raise exception 'parameter inconsistency';
                end if;

                if (ele.timestamp not between p_mints - '1 minute'::interval and p_maxts + '1 minute'::interval) then
                    drop table tt;
                    raise exception 'timestamp inconsistency';
                end if;

                select count(*) into cnt from measurementhistory t1
                where t1.timestamp = ele.timestamp and
                      t1.timeseries_id = v_timeseries_id and
                      t1.partition_id = v_partition_id and
                      (p_extkey = false or abs(t1.double_value - ele.double_value) <= p_epsilon);

                if (cnt = 0) then
                    insert into measurementhistory
                    (created_on, timestamp, double_value, timeseries_id, partition_id)
                    values (ele.created_on, ele.timestamp, ele.double_value, v_timeseries_id, v_partition_id);
                    ret[3] := ret[3] + 1;
                elsif p_extkey = false and (abs(val - ele.double_value) > p_epsilon) then
                    update measurementhistory t1 set double_value = ele.double_value
                    where t1.timestamp  = ele.timestamp  and
                          t1.timeseries_id = v_timeseries_id and
                          t1.partition_id = v_partition_id;

                    ret[2] := ret[2] + 1;
                end if;
            end loop;
        end if;

        -- loop over measurementhistory for delete

        for rec in select * from measurementhistory t1
            where t1.timeseries_id = v_timeseries_id and
                  t1.partition_id = v_partition_id and
                  t1.timestamp between p_mints and p_maxts
        loop
            select count(*) into cnt from tt t1
            where t1.timestamp = rec.timestamp and
                  t1.station_id = p_station_id and
                  t1.type_id = p_type_id and
                  t1.period = p_period and
                  (p_extkey = false or abs(t1.double_value - rec.double_value) <= p_epsilon);

            if (cnt = 0) then
                delete from measurementhistory t1
                where t1.timestamp = rec.timestamp and
                      t1.timeseries_id = v_timeseries_id and
                      t1.partition_id = v_partition_id;

                ret[1] := ret[1] + 1;
            end if;
        end loop;

        drop table tt;

        return ret;
    end;
$$ language 'plpgsql';