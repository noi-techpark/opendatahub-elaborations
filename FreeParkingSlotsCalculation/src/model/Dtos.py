class DataPoint(dict):
    def __init__(self,timestamp,value,period):
        dict.__init__(self, timestamp=timestamp, value=value, period=period,_t="it.bz.idm.bdp.dto.SimpleRecordDto")
class Provenance(dict):
    def __init__(self, uuid, lineage, collector, version):
        dict.__init__(self, uuid=uuid, lineage=lineage, dataCollector=collector, dataCollectorVersion=version)
