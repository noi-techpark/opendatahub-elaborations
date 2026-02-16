
CREATE TEMP TABLE affected_timeseries AS
    SELECT ts.id, ts.value_table FROM timeseries ts
    JOIN station s ON s.id = ts.station_id
    JOIN type t ON t.id = ts.type_id
    WHERE s.origin = 'a22-algorab'
    AND s.stationtype = 'EnvironmentStation'
    AND t.cname LIKE '%_processed';

DELETE FROM measurementhistory
WHERE timeseries_id IN (SELECT id FROM affected_timeseries where value_table = 'measurement')
AND timestamp >= '2024-03-11';

DELETE FROM measurementstringhistory
WHERE timeseries_id IN (SELECT id FROM affected_timeseries where value_table = 'measurementstring')
AND timestamp >= '2024-03-11';

DELETE FROM measurementjsonhistory
WHERE timeseries_id IN (SELECT id FROM affected_timeseries where value_table = 'measurementjson')
AND timestamp >= '2024-03-11';

update measurement
set timestamp = '2024-03-11'
WHERE timeseries_id IN (SELECT id FROM affected_timeseries where value_table = 'measurement')
AND timestamp >= '2024-03-11';

update measurementstring
set timestamp = '2024-03-11'
WHERE timeseries_id IN (SELECT id FROM affected_timeseries where value_table = 'measurementstring')
AND timestamp >= '2024-03-11';

update measurementjson
set timestamp = '2024-03-11'
WHERE timeseries_id IN (SELECT id FROM affected_timeseries where value_table = 'measurementjson')
AND timestamp >= '2024-03-11';

DROP TABLE affected_timeseries;