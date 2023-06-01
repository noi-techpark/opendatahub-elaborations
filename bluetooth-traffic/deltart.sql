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
-- This makes it possible to keep a copy of part of that table in another schema
-- for testing purposes, simply by setting the search path to that debug schema.
--
-- -----------------------------------------------------------------------------------


create or replace function intimev2.deltart
(
    p_arr         intimev2.measurementhistory[],
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

        ele intimev2.measurementhistory;
        rec intimev2.measurementhistory;
        val double precision;
        cnt bigint;
        ret int[4];

    begin

        ret[1] := 0;  -- DELete count
        ret[2] := 0;  -- upDAte count
        ret[3] := 0;  -- inseRT count
        ret[4] := coalesce(array_length(p_arr, 1),0); -- input element count, zero when null or zero length array

        if (p_extkey) then

            -- ----------------------------------------------------------------------------------------- --
            -- case 1/2: key = (station_id, type_id, period, double_value) -> insert or delete                  --
            -- ----------------------------------------------------------------------------------------- --

            create temporary table tt (
                timestamp  timestamp without time zone,
                double_value      double precision,
                station_id bigint,
                type_id    bigint,
                period     integer
            );

            if (array_length(p_arr, 1) > 0) then

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
                    where t1.timestamp  = ele.timestamp  and
                          t1.type_id    = ele.type_id    and
                          t1.period     = ele.period     and
                          t1.station_id = ele.station_id and
                          abs(t1.double_value - ele.double_value) <= p_epsilon;

                    if (cnt = 0) then

                        insert into measurementhistory
                        (created_on, timestamp, double_value, station_id, type_id, period)
                        values (ele.created_on, ele.timestamp, ele.double_value, ele.station_id, ele.type_id, ele.period);
                        ret[3] := ret[3] + 1;

                    end if;

                end loop;

            end if;

            -- loop over measurementhistory for delete

            for rec in select * from measurementhistory t1
                where t1.type_id    = p_type_id    and
                      t1.period     = p_period     and
                      t1.station_id = p_station_id and
                      t1.timestamp between p_mints and p_maxts
            loop

                select count(*) into cnt from tt t1
                where t1.timestamp  = rec.timestamp  and
                      t1.type_id    = rec.type_id    and
                      t1.period     = rec.period     and
                      t1.station_id = rec.station_id and
                      abs(t1.double_value - rec.double_value) <= p_epsilon;

                if (cnt = 0) then

                    delete from measurementhistory t1
                    where t1.timestamp  = rec.timestamp  and
                          t1.type_id    = rec.type_id    and
                          t1.period     = rec.period     and
                          t1.station_id = rec.station_id;

                    ret[1] := ret[1] + 1;

                end if;

            end loop;

        else

            -- ----------------------------------------------------------------------------------------- --
            -- case 2/2: key = (station_id, type_id, period) -> insert, update or delete                 --
            -- ----------------------------------------------------------------------------------------- --

            create temporary table tt (
                timestamp  timestamp without time zone,
                double_value      double precision,
                station_id bigint,
                type_id    bigint,
                period     integer
            );

            if (array_length(p_arr, 1) > 0) then

                -- loop over array for insert/update and copy the array into a temporary table

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

                    select double_value into val from measurementhistory t1
                    where t1.timestamp  = ele.timestamp  and
                          t1.type_id    = ele.type_id    and
                          t1.period     = ele.period     and
                          t1.station_id = ele.station_id;

                    if (not found) then

                        insert into measurementhistory
                        (created_on, timestamp, double_value, station_id, type_id, period)
                        values (ele.created_on, ele.timestamp, ele.double_value, ele.station_id, ele.type_id, ele.period);
                        ret[3] := ret[3] + 1;

                    elsif (abs(val - ele.double_value) > p_epsilon) then

                        update measurementhistory t1 set double_value = ele.double_value
                        where t1.timestamp  = ele.timestamp  and
                              t1.type_id    = ele.type_id    and
                              t1.period     = ele.period     and
                              t1.station_id = ele.station_id;

                        ret[2] := ret[2] + 1;

                    end if;

                end loop;

            end if;

            -- loop over measurementhistory for delete

            for rec in select * from measurementhistory t1
                where t1.type_id    = p_type_id    and
                      t1.period     = p_period     and
                      t1.station_id = p_station_id and
                      t1.timestamp between p_mints and p_maxts
            loop

                select double_value into val from tt t1
                where t1.timestamp  = rec.timestamp  and
                      t1.type_id    = rec.type_id    and
                      t1.period     = rec.period     and
                      t1.station_id = rec.station_id;

                if (not found) then

                    delete from measurementhistory t1
                    where t1.timestamp  = rec.timestamp  and
                          t1.type_id    = rec.type_id    and
                          t1.period     = rec.period     and
                          t1.station_id = rec.station_id;

                    ret[1] := ret[1] + 1;

                end if;

            end loop;

        end if;

        drop table tt;

        return ret;

    end;
$$ language 'plpgsql';
