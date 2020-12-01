class DataPoint(dict):
    def __init__(self,timestamp,value,period):
        dict.__init__(self, timestamp=timestamp, value=value, period=period,_t="it.bz.idm.bdp.dto.SimpleRecordDto")
