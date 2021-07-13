from keycloak import KeycloakOpenID
import requests
import json
import os
from model.Dtos import Provenance

# Configure client
keycloak_openid = KeycloakOpenID(server_url= os.getenv("AUTHENTICATION_SERVER"),
                    client_id="odh-a22-dataprocessor",
                    realm_name="noi",
                    client_secret_key=os.getenv("CLIENT_SECRET"),
                    verify=True)


class DataPusher:
    def __init__(self):
        self.provenance_id = None
        self.token = keycloak_openid.token("", "","client_credentials")
        self.upsert_provenance()

    def send_data(self,station_type, data_map):
        data_map["provenance"]= self.provenance_id
        endpoint = os.getenv("ODH_SHARE_ENDPOINT")+"/json/pushRecords/" + station_type
        r = requests.post(endpoint, json=data_map, headers={"Authorization" : "Bearer " + self.token['access_token']})
        if (r.status_code != 201):
            print("Status code not 201 but " + str(r.status_code))
            print(data_map)
    
    def upsert_provenance(self):
        collector = os.getenv("PROVENANCE_NAME")
        version = os.getenv("PROVENANCE_VERSION")
        lineage = os.getenv("PROVENANCE_LINEAGE")
        p = Provenance(None, lineage, collector, version)
        r = requests.post(os.getenv("ODH_SHARE_ENDPOINT")+"/json/provenance", json= p, headers={"Authorization" : "Bearer " + self.token['access_token']})
        self.provenance_id = r.text
