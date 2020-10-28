package it.bz.odh.elaborations.services;

import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Map;

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
                        !elaborationTypeMap.getBranch().get(typeMapEntry.getKey()).getBranch().isEmpty())
                    data = elaborationTypeMap.getBranch().get(typeMapEntry.getKey()).getData();
                startElaboration(stationMapEntry.getKey(),typeMapEntry.getKey(), !data.isEmpty() ? data.get(0).getValue().toString():null);
            }
        }
    }

    private void startElaboration(String station, String type, String lastElaborationDateString) {
        List<SimpleRecordDto> stationData = null;
        try {
            if (lastElaborationDateString!=null) {
                stationData = odhParser.getStationData(station,type,lastElaborationDateString);
            }
            else
                stationData = odhParser.getStationData(station,type);
            
            List<SimpleRecordDto> averageElaborations = elaborationService.calcAverage(stationData,Calendar.HOUR);
            DataMapDto<RecordDtoImpl> dto = new DataMapDto<RecordDtoImpl>();
            dto.addRecords(station, type, averageElaborations);
            webClient.pushData(dto);
        } catch (ParseException e) {
            e.printStackTrace();
        }
    }
}
