import requests
import os
import logging
from ODHKeyCloakClient import KeycloakClient

log = logging.getLogger()
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

class DataFetcher:
    def __init__(self):
        self.token = KeycloakClient.getDefaultInstance().token("", "","client_credentials")
        log.debug("Token created:")
        log.debug(self.token)

    def fetch_data(self, endpoint):
        r = requests.get(
            os.getenv("ODH_MOBILITY_API_NINJA") + endpoint,
            headers={"Authorization" : "Bearer " + self.token['access_token']}
        )
        if (r.status_code != 200):
            log.warn("Status code not 200 but " + str(r.status_code))
        else:
            return r.json()

    def get_newest_data_timestamps(self):
        response = self.fetch_data(
            "/tree/EnvironmentStation/*/latest?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab,mperiod.eq.3600&select=mvalidtime,scode&limit=-1")
        if (response != None):
            log.debug("fetched newest data for raw and processed data:" + str(response))
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
            log.debug("Generated station map: " + str(station_map))
            return station_map

    def get_raw_history(self, station_id, start, end):
        raw_data_map = {}
        data = self.fetch_data( "/flat/EnvironmentStation/*/"
        + str(start).replace(" ","T") + "/"+ str(end).replace(" ","T")
        + "?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab,mperiod.eq.3600,scode.eq."
        + station_id + "&select=mvalidtime,mvalue,tname")['data']
        if data != None:
            log.debug("fetched history data:" + str(data))
            for record in data:
                type_arr = str(record['tname']).split("_")
                if len(type_arr)>1 and type_arr[1] == "raw":
                    value = record['mvalue']
                    type_id = type_arr[0]
                    time = record['mvalidtime']
                    typeMap = {}
                    typeMap[type_id] = value
                    raw_data_map.setdefault(time,{}).update(typeMap)
        log.debug("Raw history: " + str(raw_data_map))
        return raw_data_map
