# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
from model.Dtos import DataPoint, DataType
from ODHAPIClient import DataFetcher
from ODHPusher import DataPusher
from ParameterImporter import getParameters

import json
import numpy as np
import logging

DEFAULT_START_CALC = "2016-01-01 00:00:00.000+0000"
NO2 = "NO2-Alphasense"
NO = "NO-Alphasense"
CO = "CO"
O3 = "O3"
RH = "RH"
PM10 = "PM10"
PM25 = "PM2.5"
T_INT = "temperature-internal"
TYPES_TO_ELABORATE = [O3,NO2,NO,PM10,PM25,CO]
TYPES_TO_REQUEST = TYPES_TO_ELABORATE + [T_INT,RH]
PARAMETER_MAP = getParameters()
log = logging.getLogger()

fetcher = DataFetcher()
pusher = DataPusher()

def parseODHTime(time: str) -> datetime:
    return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f%z")

class Processor:
    def calc_by_station(self):
        pusher.sync_datatypes([
            DataType("O3_processed","ug/m3", "O3", "Mean"),
            DataType("PM10_processed","ug/m3", "PM10", "Mean"),
            DataType("PM2.5_processed","ug/m3", "PM2.5", "Mean"),
            DataType("NO-Alphasense_processed", "ug/m3", "NO (Alphasense)", "Mean"),
            DataType("NO2-Alphasense_processed", "ug/m3", "NO2 (Alphasense)", "Mean"),
            DataType("CO_processed", "mg/m3", "CO", "Mean"),
        ])
        
        time_map = fetcher.get_newest_data_timestamps(types=TYPES_TO_ELABORATE)
        for s_id in time_map:
            start = datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)
            end = parseODHTime(DEFAULT_START_CALC)
            for t_id in time_map[s_id]['types']:
                state_map = time_map[s_id]['types'][t_id]
                end = max(parseODHTime(state_map.get('raw')), end)
                start = min(parseODHTime(state_map.get('processed', DEFAULT_START_CALC)), start)
            sensor_history = time_map[s_id]['sensor_history']

            # Process in 1-year batches to not overload API
            current_start = start
            batch_end = end + datetime.timedelta(0, 3)
            
            while current_start < batch_end:
                current_end = min(current_start + datetime.timedelta(days=365), batch_end)
                timeseries = fetcher.get_raw_history(s_id, current_start, current_end, types=TYPES_TO_REQUEST)
                
                if timeseries:
                    elaborations = self.calc(timeseries, sensor_history, s_id)
                    try:
                        pusher.send_data("EnvironmentStation", elaborations)
                    except Exception as e:
                        log.error("Failed to send data for station: " + s_id)
                        raise
                
                current_start = current_end

    def calc(self, timeseries, sensor_history, station_id):
        station_map = {"branch":{ station_id:{"branch":{},"data":[],"name":"default"}}}
        sensor_idx = -1
        sensor_end = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
        sensor_start = None
        sensor_id = ""
        for timestr in timeseries:
            time = parseODHTime(timestr)
            # Find next potential sensor history entry
            while sensor_end < time:
                sensor_idx+=1
                if sensor_history == None or sensor_idx >= len(sensor_history):
                    log.warn("Sensor history not found for station " + station_id + " at time " + str(time))
                    # our current record is past the end of sensor history
                    return station_map 
                sensor_start = datetime.datetime.strptime(sensor_history[sensor_idx]["start"], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
                sensor_end = datetime.datetime.strptime(sensor_history[sensor_idx]["end"], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc) if sensor_history[sensor_idx]["end"] != "" else datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)
                sensor_id = sensor_history[sensor_idx]["id"]
            # If the window starts after our time, or if the window doesn't have a sensor associated, discard the record
            if time < sensor_start or sensor_id == "":
                log.warn("No sensor associated for " + station_id + " at time " + str(time))
                continue
            elabs = self.process_single_dataset(timeseries[timestr], sensor_id, time)
            if elabs != None:
                for type_id in elabs:
                    type_data = station_map['branch'][station_id]["branch"].get(type_id)
                    if type_data == None: 
                        station_map['branch'][station_id]["branch"][type_id] = {"data":[elabs[type_id]],"branch":{},"name":"default"}
                    else:
                        type_data["data"].append(elabs[type_id])
        return station_map
    
    def process_single_dataset(self, data, sensor_id, time):
        T_INT = "temperature-internal"
        if T_INT in data:
            temparature_key = "hightemp" if (data[T_INT] >= 35) else "lowtemp"
            data_point_map = {}
            for type_id in (value for value in data if value in TYPES_TO_ELABORATE): #Intersection
                # ignore stations/types missing parameters #32
                if PARAMETER_MAP.get(sensor_id) is None or PARAMETER_MAP[sensor_id].get(type_id) is None:
                    continue

                value = data[type_id]
                processed_value = None
                parameters = PARAMETER_MAP[sensor_id][type_id][temparature_key]
                if ((type_id == NO2 or type_id == NO) and O3 in data and T_INT in data):
                    if(int(parameters["calc_version"]) == 1):
                        processed_value = (
                            float(parameters["a"]) 
                            + np.multiply(float(parameters["b"]), np.power(float(value),2)) 
                            + np.multiply(float(parameters["c"]), float(value)) 
                            + np.multiply(float(parameters["d"]), np.power(float(data[O3]), 0.1))
                            + np.multiply(float(parameters["e"]), np.power(data[T_INT],4))
                        ) 
                    else:
                        processed_value = (
                            float(parameters["a"]) 
                            + np.multiply(float(parameters["b"]), np.power(float(value),2)) 
                            + np.multiply(float(parameters["c"]), float(value)) 
                            + np.multiply(float(parameters["d"]), float(data[O3]))
                            + np.multiply(float(parameters["e"]), np.power(data[T_INT],4))
                        )
                elif ((type_id == PM10 or type_id == PM25) and all (tid in data for tid in (RH,PM10,T_INT))
                        and not (data[T_INT] >= 35 and data[PM10]>100) and not(data[T_INT] < 35 and data[RH]>97)):
                    processed_value = (
                        float(parameters["a"])
                        + float(parameters["b"]) * np.power(float(value),0.7)
                        + float(parameters["c"]) * np.power(float(data[RH]),0.75)
                        + float(parameters["d"]) * np.power(float(data[T_INT]),0.3)
                    )
                elif (type_id == O3 and all (t_id in data for t_id in (RH,T_INT,NO2))):
                    processed_value = (
                        float(parameters["a"])
                        + float(parameters["b"]) * np.power(float(value), 0.44)
                        + float(parameters["c"]) * np.power(float(data[NO2]),0.58)
                        + float(parameters["d"]) * np.power(float(data[RH]),0.54)
                        + float(parameters["e"]) * np.power(float(data[T_INT]),1.2)
                    )
                elif (type_id == CO and all (t_id in data for t_id in (RH,T_INT))):
                    processed_value = (
                        float(parameters["a"])
                        + float(parameters["b"]) * float(value)
                        + float(parameters["c"]) * np.power(float(data[T_INT]),0.1)
                        + float(parameters["d"]) * np.power(float(data[RH]),0.1)
                    )
                else:
                    log.warn("Conditions were not met to do calculation for sensor: " 
                    + sensor_id + " type:" + type_id + " at " + time.ctime() + " on this dataset:")
                    log.warn(data)
                if processed_value != None and not math.isnan(processed_value) and not math.isinf(processed_value):
                    if processed_value < 0:
                        processed_value = 0
                    odhtimestamp = time.timestamp() * 1000
                    data_point_map[type_id+"_processed"] = DataPoint(odhtimestamp, processed_value, 3600)
                    processed_value = None
            return data_point_map
