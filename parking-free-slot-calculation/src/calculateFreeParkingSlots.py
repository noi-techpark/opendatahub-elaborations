import requests
import datetime
from datetime import timezone
from model.Dtos import DataPoint
from odh_pusher import DataPusher
import os


d = DataPusher()
class FreeParkingSlotsCalculator:

    OCCUPIED_URL = "/flat/ParkingStation,ParkingSensor/occupied/latest?limit=-1&where=sactive.eq.true&select=mvalidtime,tname,scode,stype,smetadata,mperiod"
    FREE_URL = "/flat/ParkingStation,ParkingSensor/free/latest?limit=-1&where=sactive.eq.true&select=mvalidtime,tname,scode,stype,mperiod"

    def fetchData(self, url):
        r = requests.get(os.getenv("ODH_MOBILITY_API_NINJA") + url)
        return r.json()['data'];

    def getHistoryData(self, stationcode, period, fromTime):
        fromDate = fromTime.strftime("%Y-%m-%d")
        toDate = (fromTime+datetime.timedelta(weeks=+4)).strftime("%Y-%m-%d")
        #print("Interval:"+fromDate+"-"+toDate)
        fetchUrl = "/flat/ParkingStation,ParkingSensor/occupied/"+fromDate+"/"+toDate+"?limit=-1&where=scode.eq.\""+stationcode+"\",mperiod.eq." + str(period) + "&select=tmeasurements"
        #print(fetchUrl)
        return self.fetchData(fetchUrl)

    def sendToOdh(self,stationType,station,data):
        d.pushData(stationType,station,"free",data)

    def calculateFreeParkingLots(self,stationType, station, period, capacity, fromDate,newestRawDataTimestamp):
        if fromDate < newestRawDataTimestamp:
            history = self.getHistoryData(station,period,fromDate)
            calculatedPoints = []
            for dataPoint in history:
                free = capacity - dataPoint['mvalue']
                timestamp =  datetime.datetime.strptime(dataPoint['mvalidtime'], '%Y-%m-%d %H:%M:%S.%f%z').timestamp()*1000
                calculatedPoints.append(DataPoint(timestamp,free,period))
            if (len(calculatedPoints)>0):
                self.sendToOdh(stationType, station,calculatedPoints)
            later = fromDate + datetime.timedelta(weeks=+4)
            self.calculateFreeParkingLots(stationType, station, period, capacity, later, newestRawDataTimestamp)

    def startCalculations(self):
        d.upsertProvenance()
        occupiedSlots = self.fetchData(self.OCCUPIED_URL)
        freeSlots = self.fetchData(self.FREE_URL)
        for station in occupiedSlots:
            try:
                sId = station['scode']
                if (station['stype'] == "ParkingSensor"):
                    capacity = 1
                else:
                    capacity = station['smetadata']['capacity']
                newestRawDataTimestamp = datetime.datetime.strptime(station['mvalidtime'], '%Y-%m-%d %H:%M:%S.%f%z')
                tmpFreeSlots = [s for s in freeSlots if (s['scode'] == sId and s['mperiod']==station['mperiod'])]
                if len(tmpFreeSlots) == 1 :
                    lastElaborationTimestamp = datetime.datetime.strptime(tmpFreeSlots[0]['mvalidtime'], '%Y-%m-%d %H:%M:%S.%f%z')
                    print("Last Elaboration for station "+str(sId) + " is " +lastElaborationTimestamp.strftime("%Y-%m-%d %H:%M:%S.%f%z"))
                else:
                    lastElaborationTimestamp = datetime.datetime(2013,2,1, tzinfo= timezone.utc)
                    print("No elaboration for station "+str(sId) + " default value= " + lastElaborationTimestamp.strftime("%Y-%m-%d %H:%M:%S.%f%z"))
                print("Newest Raw data timestamp:"+station['mvalidtime'])
                self.calculateFreeParkingLots(station['stype'],sId,station['mperiod'],capacity,lastElaborationTimestamp,newestRawDataTimestamp)
            except KeyError as e:
                print(repr(e))
                print("Raw data is missing for station:"+sId)
                continue


