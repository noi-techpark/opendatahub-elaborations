import datetime
from datetime import timezone
from model.Dtos import DataPoint
from ODHAPIClient import DataFetcher
from ODHPusher import DataPusher

import json
import numpy as np

DEFAULT_START_CALC = "2016-01-01 00:00:00.000+0000"
NO2 = "NO2-Alphasense"
NO = "NO-Alphasense"
O3 = "O3"
RH = "RH"
PM10 = "PM10"
PM25 = "PM2.5"
T_INT = "temperature-internal"
TYPES_TO_ELABORATE = [O3,NO2,NO,PM10,PM25]
F = open('data.json',)
PARAMETER_MAP = json.load(F)

fetcher = DataFetcher()
pusher = DataPusher()
class Processor:
    def calc_by_station(self):
        time_map = fetcher.get_newest_data_timestamps()
        for s_id in time_map:
            start = datetime.datetime.now(timezone.utc)
            for t_id in time_map[s_id]:
                state_map = time_map[s_id][t_id]
                end_time = state_map.get('raw')
                start_time = datetime.datetime.strptime(state_map.get('processed',DEFAULT_START_CALC),"%Y-%m-%d %H:%M:%S.%f%z")
                if (start > start_time):
                    start = start_time
            print(start)
            print(end_time)
            history = fetcher.get_raw_history(s_id,start,end_time)
            elaborations = self.calc(history,s_id)
            pusher.send_data("EnvironmentStation",elaborations)
    def calc(self, history,station_id):
        station_map ={"branch":{ station_id:{"branch":{},"data":[],"name":"default"}}}
        for time in  history:
            elabs = self.calc_single_time(history[time], station_id, time)
            if elabs != None:
                for type_id in elabs:
                    type_data = station_map['branch'][station_id]["branch"].get(type_id)
                    if type_data == None: 
                        station_map['branch'][station_id]["branch"][type_id] = {"data":[elabs[type_id]],"branch":{},"name":"default"}
                    else:
                        type_data["data"].append(elabs[type_id])
        return station_map
    
    def calc_single_time(self, data, station_id, time):
        T_INT = "temperature-internal"
        if T_INT in data:
            temparature_key = "hightemp" if (data[T_INT] >= 20) else "lowtemp"
            data_point_map = {}
            for type_id in (value for value in data if value in TYPES_TO_ELABORATE): #Intersection
                value = data[type_id]
                processed_value = None               
                station_id_short =str(station_id).split("_")[1]
                if ((type_id == NO2 or type_id == NO) and O3 in data and T_INT in data):
                    parameters = PARAMETER_MAP[station_id_short][type_id][temparature_key]
                    processed_value = (float(parameters["a"]) + np.multiply(float(parameters["b"]),np.power(float(value),2)) + 
                    float(parameters["c"]) * float(value) + 
                    np.multiply(float(parameters["d"]),np.power(float(data[O3]),0.1))
                    + np.multiply(float(parameters["e"]),np.power(data[T_INT],4))
                    )
                elif ((type_id == PM10 or type_id == PM25) and all (tid in data for tid in (RH,PM10,T_INT))
                        and not (data[T_INT] >= 20 and data[PM10]>100) and not(data[T_INT] < 20 and data[RH]>97)):
                    parameters = PARAMETER_MAP[station_id_short][type_id][temparature_key]
                    processed_value = float(parameters["a"]) + float(parameters["b"]) * np.power(float(value),0.7) 
                    + float(parameters["c"]) * np.power(float(data[RH]),0.75)
                    + float(parameters["d"]) * np.power(float(data[T_INT]),0.3)
                elif (type_id == O3 and all (t_id in data for t_id in (RH,T_INT,NO2))):
                    parameters = PARAMETER_MAP[station_id_short][type_id][temparature_key]
                    processed_value = (float(parameters["a"]) + float(parameters["b"]) * np.power(float(value), 0.44) 
                    + float(parameters["c"]) * np.power(float(data[NO2]),0.58) + 
                    float(parameters["d"]) * np.power(float(data[RH]),0.54)
                    + float(parameters["e"]) * np.power(float(data[T_INT]),1.2))
                else:
                    print("Conditions were not met to do calculation for: " + type_id + " at " + time + " on this dataset:")
                    print(data)
                if processed_value != None:
                    data_point_map[type_id+"_processed"] = DataPoint(datetime.datetime.strptime(time,"%Y-%m-%d %H:%M:%S.%f%z").timestamp() * 1000,processed_value,3600)
                    processed_value = None
            return data_point_map
