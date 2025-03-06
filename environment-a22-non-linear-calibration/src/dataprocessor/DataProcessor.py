# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
from model.Dtos import DataPoint
from ODHAPIClient import DataFetcher
from ODHPusher import DataPusher
from ParameterImporter import getParameters

import json
import numpy as np
import logging

DEFAULT_START_CALC = "2016-01-01 00:00:00.000+0000"
NO2 = "NO2-Alphasense"
NO = "NO-Alphasense"
O3 = "O3"
RH = "RH"
PM10 = "PM10"
PM25 = "PM2.5"
T_INT = "temperature-internal"
TYPES_TO_ELABORATE = [O3,NO2,NO,PM10,PM25]
TYPES_TO_REQUEST = TYPES_TO_ELABORATE + [T_INT] # Temperature is required by calc, even though it's not elaborated
PARAMETER_MAP = getParameters()
STATIONS_TO_ELABORATE = list(PARAMETER_MAP.keys())
log = logging.getLogger()

fetcher = DataFetcher()
pusher = DataPusher()

def parseODHTime(time: str) -> datetime:
    return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f%z")

class Processor:
    def calc_by_station(self):
        time_map = fetcher.get_newest_data_timestamps(stations=STATIONS_TO_ELABORATE, types=TYPES_TO_ELABORATE)
        for s_id in time_map:
            
            start = datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)
            end = parseODHTime(DEFAULT_START_CALC)
            for t_id in time_map[s_id]:
                state_map = time_map[s_id][t_id]
                end = max(parseODHTime(state_map.get('raw')), end)
                start = min(parseODHTime(state_map.get('processed', DEFAULT_START_CALC)), start)
            history = fetcher.get_raw_history(s_id, start, end+datetime.timedelta(0, 3), types=TYPES_TO_REQUEST)
            if history:
                elaborations = self.calc(history,s_id)
                pusher.send_data("EnvironmentStation", elaborations)
    def calc(self, history, station_id):
        station_map = {"branch":{ station_id:{"branch":{},"data":[],"name":"default"}}}
        for time in history:
            elabs = self.process_single_dataset(history[time], station_id, time)
            if elabs != None:
                for type_id in elabs:
                    type_data = station_map['branch'][station_id]["branch"].get(type_id)
                    if type_data == None: 
                        station_map['branch'][station_id]["branch"][type_id] = {"data":[elabs[type_id]],"branch":{},"name":"default"}
                    else:
                        type_data["data"].append(elabs[type_id])
        return station_map
    
    def process_single_dataset(self, data, station_id, time):
        T_INT = "temperature-internal"
        if T_INT in data:
            temparature_key = "hightemp" if (data[T_INT] >= 20) else "lowtemp"
            data_point_map = {}
            for type_id in (value for value in data if value in TYPES_TO_ELABORATE): #Intersection
                # ignore stations/types missing parameters #32
                if PARAMETER_MAP.get(station_id) is None or PARAMETER_MAP[station_id].get(type_id) is None:
                    continue

                value = data[type_id]
                processed_value = None
                parameters = PARAMETER_MAP[station_id][type_id][temparature_key]
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
                        and not (data[T_INT] >= 20 and data[PM10]>100) and not(data[T_INT] < 20 and data[RH]>97)):
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
                else:
                    log.warn("Conditions were not met to do calculation for station: " 
                    + station_id + " type:" + type_id + " at " + time + " on this dataset:")
                    log.warn(data)
                if processed_value != None:
                    if processed_value < 0:
                        processed_value = 0
                    odhtimestamp = parseODHTime(time).timestamp() * 1000
                    data_point_map[type_id+"_processed"] = DataPoint(odhtimestamp, processed_value, 3600)
                    if type_id == "NO2-Alphasense":
                        if processed_value >= 40:
                            public_value = "very bad"
                        elif processed_value > 30:
                            public_value = "bad"
                        elif processed_value > 20:
                            public_value = "pretty good"
                        elif processed_value > 10:
                            public_value = "good"
                        else:
                            public_value = "very good"
                        data_point_map[type_id+"_processed_public"] = DataPoint(odhtimestamp, public_value, 3600)
                    processed_value = None
            return data_point_map
