import requests
import os
from ODHKeyCloakClient import KeycloakClient

class DataFetcher:
    def __init__(self):
        self.token = KeycloakClient.getDefaultInstance().token("", "","client_credentials")

    def create_data_map(self,station,dataType,dataPoints):
        dataMap = {"name":"(default)","branch":{},"data": dataPoints}
        typeMap = {"name":"(default)","branch": {dataType:dataMap},"data":[]}
        stationMap = {"name":"(default)","branch":{station:typeMap},"data":[], "provenance": self.provenanceId}
        return stationMap

    def fetch_data(self, endpoint):
        r = requests.get(os.getenv("RAW_DATA_ENDPOINT") + endpoint,headers={"Authorization" : "Bearer " + self.token['access_token']})
        if (r.status_code != 200):
            print("Status code not 200 but " + str(r.status_code))
        else: 
            return r.json()

    def get_newest_data_timestamps(self):
        response = self.fetch_data(
            "/tree/EnvironmentStation/*/latest?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab,mperiod.eq.3600&select=mvalidtime,scode&limit=-1")
        if (response != None):
            stations = response['data']['EnvironmentStation']['stations']
            station_map = {}
            for station_id in stations:                
                station_types = stations[station_id]['sdatatypes']
                type_map = {}
                station_map[station_id]= type_map
                for type_id in station_types:
                    newest_record_timestamp = station_types[type_id]['tmeasurements'][0]['mvalidtime']
                    type_split = str(type_id).split("_")
                    state = type_map.get(type_split[0],{})
                    state[type_split[1]] = newest_record_timestamp
                    type_map[type_split[0]] = state
            return station_map

    def get_raw_history(self, station_id, start, end):
        elab_map = {}
        data = self.fetch_data( "/flat/EnvironmentStation/*/" 
        + str(start).replace(" ","T") + "/"+ str(end).replace(" ","T") 
        + "?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab,mperiod.eq.3600,scode.eq."
        + station_id + "&select=mvalidtime,mvalue,tname")['data']
        for record in data:
            type_arr = str(record['tname']).split("_")
            if len(type_arr)>1 and type_arr[1] == "raw":
                value = record['mvalue']
                type_id = type_arr[0]
                time = record['mvalidtime']
                typeMap = {}
                typeMap[type_id] = value 
                elab_map.setdefault(time,{}).update(typeMap)
        return elab_map
