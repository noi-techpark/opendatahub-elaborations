package it.bz.odh.elaborations.services;

import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang.time.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import it.bz.idm.bdp.dto.DataMapDto;
import it.bz.idm.bdp.dto.RecordDtoImpl;
import it.bz.idm.bdp.dto.SimpleRecordDto;

@Service
public class JobScheduler {

    @Autowired
    private ODHParser odhParser;

    @Autowired
    private ElaborationService elaborationService;

    @Autowired
    private ODHWriterClient webClient;

    public void executeElaborations() {

        DataMapDto<RecordDtoImpl> dataMap = odhParser.createDataMap();
        DataMapDto<RecordDtoImpl> newestElaborationMap = odhParser.createNewestElaborationMap();

        for (Map.Entry<String, DataMapDto<RecordDtoImpl>> stationMapEntry : dataMap.getBranch().entrySet()) {
            for (Map.Entry<String, DataMapDto<RecordDtoImpl>> typeMapEntry : stationMapEntry.getValue().getBranch().entrySet()) {
                List<RecordDtoImpl> data = new ArrayList<RecordDtoImpl>();
                DataMapDto<RecordDtoImpl> elaborationTypeMap = newestElaborationMap.getBranch().get(stationMapEntry.getKey());
                if (!newestElaborationMap.getBranch().isEmpty() && 
                        elaborationTypeMap != null &&
                        !elaborationTypeMap.getBranch().isEmpty() && 
                        elaborationTypeMap.getBranch().get(typeMapEntry.getKey()) != null && 
                        !elaborationTypeMap.getBranch().get(typeMapEntry.getKey()).getData().isEmpty())
                    data = elaborationTypeMap.getBranch().get(typeMapEntry.getKey()).getData();

                List<RecordDtoImpl> rawData = dataMap.getBranch().get(stationMapEntry.getKey()).getBranch().get(typeMapEntry.getKey()).getData();
                Long lastElaborationDateUTC = !data.isEmpty() ? data.get(0).getTimestamp():null;
                Long lastRawDateUTC = rawData.get(0).getTimestamp();
                if (lastElaborationDateUTC == null || lastRawDateUTC-(3600*1000) > lastElaborationDateUTC)  //start elaborations only if there is new data of one hour
                    startElaboration(stationMapEntry.getKey(),typeMapEntry.getKey(), lastElaborationDateUTC,lastRawDateUTC);
            }
        }
    }

    private void startElaboration(String station, String type, Long lastElaborationDateUTC, Long lastRawDateUTC) {
        List<SimpleRecordDto> stationData = null;
        try {
            if (lastElaborationDateUTC != null) {
                stationData = odhParser.getStationData(station,type,lastElaborationDateUTC);
            }
            else
                stationData = odhParser.getStationData(station,type);
            if (!stationData.isEmpty()) {
                List<SimpleRecordDto> averageElaborations = elaborationService.calcAverage(stationData,Calendar.HOUR);
                if (!averageElaborations.isEmpty()) {
                    DataMapDto<RecordDtoImpl> dto = new DataMapDto<RecordDtoImpl>();
                    dto.addRecords(station, type, averageElaborations);

                    webClient.pushData(dto);
                    Long newOldestElaboration = DateUtils.ceiling(new Date(averageElaborations.get(averageElaborations.size()-1).getTimestamp()),Calendar.HOUR).getTime();
                    if (newOldestElaboration <= lastRawDateUTC)
                        startElaboration(station, type, newOldestElaboration, lastRawDateUTC);
                }
            }
        } catch (ParseException e) {
            e.printStackTrace();
        }
    }
}
