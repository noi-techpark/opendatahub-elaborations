
create temporary table holidays as
select sub.date                                          as ts,
       exists(select *
              from sta_planned_data.day_type_assignment dta
                       join sta_planned_data.day_type_favorites_mapping_mvw dt
                            on dt.id_version_original = dta.day_type_ref and dt.publication_timestamp = dta.publication_timestamp
              where dta.date = sub.date
                and dt.favorites_short_name = 's')::int  as is_school,
       exists(select *
              from sta_planned_data.day_type_assignment dta
                       join sta_planned_data.day_type_favorites_mapping_mvw dt
                            on dt.id_version_original = dta.day_type_ref and dt.publication_timestamp = dta.publication_timestamp
              where dta.date = sub.date
                and dt.favorites_short_name = 'T3')::int as is_holiday
from (select distinct date from sta_planned_data.day_type_assignment where date >= '2022-01-01') as sub
order by date;
\copy holidays to 'data-holidays/holidays.csv' with csv header

