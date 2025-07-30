# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
import os
import logging
from ODHKeyCloakClient import KeycloakClient
from functools import reduce

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

    def get_newest_data_timestamps(self, types):
        # each type is requested with _raw and _processed postfix, e.g. "NO2" becomes "NO2_raw,NO2_processed"
        types_to_fetch = ",".join([tp + postfix for tp in types for postfix in ["_raw", "_processed"]])
        response = self.fetch_data(f"/tree/EnvironmentStation/{types_to_fetch}/latest"
            "?select=mvalidtime,scode,smetadata.sensor_history"
            "&where=sactive.eq.true"
                ",sorigin.eq.a22-algorab"
                ",mperiod.eq.3600"
            "&limit=-1"
            )
        if (response != None):
            log.debug("fetched newest data for raw and processed data:" + str(response))
            stations = response['data']['EnvironmentStation']['stations']
            station_map = {}
            for station_id in stations:
                station_types = stations[station_id]['sdatatypes']
                type_map = {}
                for type_id in station_types:
                    newest_record_timestamp = station_types[type_id]['tmeasurements'][0]['mvalidtime']
                    type_split = str(type_id).split("_")
                    state = type_map.get(type_split[0],{})
                    state[type_split[1]] = newest_record_timestamp
                    type_map[type_split[0]] = state
                station_map[station_id] = {
                    'types': type_map,
                    'sensor_history': stations[station_id]['smetadata']['sensor_history']
                }
            log.debug("Generated station map: " + str(station_map))
            return station_map

    def get_raw_history(self, station_id, start, end, types):
        raw_data_map = {}
        types_str = ",".join(map(lambda x : x + "_raw", types))
        start_str = str(start).replace(" ","T")
        end_str = str(end).replace(" ","T")
        req_path = (f"/flat/EnvironmentStation/{types_str}/{start_str}/{end_str}" +
            "?select=mvalidtime,mvalue,tname"
            "&where=sactive.eq.true"
                ",sorigin.eq.a22-algorab"
                ",mperiod.eq.3600"
                ",scode.eq." + station_id + 
            "&limit=-1")
        try:
            data = self.fetch_data(req_path)['data']
            if data:
                log.debug("fetched history data:" + str(data))
                for record in data:
                    value = record['mvalue']
                    type_id = str(record['tname']).split("_")[0]
                    time = record['mvalidtime']
                    typeMap = {}
                    typeMap[type_id] = value
                    raw_data_map.setdefault(time,{}).update(typeMap)
            log.debug("Raw history: " + str(raw_data_map))
        except Exception as e:
            log.error("Failed requesting raw history: %s", req_path, exc_info=e)
            raise
        return raw_data_map
