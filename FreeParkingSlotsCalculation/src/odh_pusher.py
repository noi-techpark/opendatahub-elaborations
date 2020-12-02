from keycloak import KeycloakOpenID
import requests
import json
import os
from model.Dtos import DataPoint,Provenance

# Configure client
keycloak_openid = KeycloakOpenID(server_url= os.getenv("AUTHENTICATION_SERVER"),
                    client_id="odh-elaborations-lambda",
                    realm_name="noi",
                    client_secret_key=os.getenv("CLIENT_SECRET"),
                    verify=True)


class DataPusher:
    def __init__(self):
        self.provenanceId = None

    def pushData(self,stationType,stationCode,dataType,dataPoints):
        dataMap = self.createDataMap(stationCode,dataType,dataPoints)
        self.sendData(stationType,dataMap)

    def createDataMap(self,station,dataType,dataPoints):
        dataMap = {"name":"(default)","branch":{},"data": dataPoints}
        typeMap = {"name":"(default)","branch": {dataType:dataMap},"data":[]}
        stationMap = {"name":"(default)","branch":{station:typeMap},"data":[], "provenance": self.provenanceId}
        return stationMap

    def sendData(self,stationType, dataMap):
        token = keycloak_openid.token("", "","client_credentials")
        r = requests.post(os.getenv("ODH_SHARE_ENDPOINT")+"/json/pushRecords/"+stationType, json=dataMap, headers={"Authorization" : "Bearer " + token['access_token']})
        if (r.status_code != 201):
            print("Status code not 201 but " + str(r.status_code))
    
    def upsertProvenance(self):
        collector = os.getenv("PROVENANCE_NAME")
        version = os.getenv("PROVENANCE_VERSION")
        lineage = os.getenv("PROVENANCE_LINEAGE")
        p = Provenance(None, lineage, collector, version)
        token = keycloak_openid.token("", "","client_credentials")
        r = requests.post(os.getenv("ODH_SHARE_ENDPOINT")+"/json/provenance", json= p, headers={"Authorization" : "Bearer " + token['access_token']})
        self.provenanceId = r.text
