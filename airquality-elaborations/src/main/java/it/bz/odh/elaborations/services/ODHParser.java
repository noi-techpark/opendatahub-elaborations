package it.bz.odh.elaborations.services;

import java.text.ParseException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import it.bz.idm.bdp.dto.DataMapDto;
import it.bz.idm.bdp.dto.RecordDtoImpl;
import it.bz.idm.bdp.dto.SimpleRecordDto;

@Service
public class ODHParser {

    @Autowired
    private ODHReaderClient client;
    
    public DataMapDto<RecordDtoImpl> createDataMap() {
        LinkedHashMap<String,Object> ninjaTree = (LinkedHashMap<String, Object>) ((LinkedHashMap<String, Object>) client.getLatestNinjaTree().get("data")).get("EnvironmentStation");
        LinkedHashMap<String,Object> stations = (LinkedHashMap<String, Object>) ninjaTree.get("stations");
        DataMapDto<RecordDtoImpl> dto = new DataMapDto<RecordDtoImpl>();
        for (Map.Entry<String, Object> station : stations.entrySet()) {
            DataMapDto<RecordDtoImpl> typeMap = new DataMapDto<RecordDtoImpl>();
            LinkedHashMap<String,Object> typesContainer= parseMap(station.getValue());
            LinkedHashMap<String, Object> types = parseMap(typesContainer.get("sdatatypes"));
            for (Map.Entry<String, Object> type : types.entrySet())
                typeMap.upsertBranch(type.getKey());
            dto.getBranch().put(station.getKey(), typeMap);
        }
        return dto;
    }
    public DataMapDto<RecordDtoImpl> createNewestElaborationMap() {
        DataMapDto<RecordDtoImpl> dto = new DataMapDto<RecordDtoImpl>();
        LinkedHashMap<String, Object> dataSet = (LinkedHashMap<String, Object>) client.createNewestElaborationMap().get("data");
        if (!dataSet.isEmpty()) {
            LinkedHashMap<String,Object> ninjaTree = (LinkedHashMap<String, Object>) dataSet.get("EnvironmentStation");
            LinkedHashMap<String,Object> stations = (LinkedHashMap<String, Object>) ninjaTree.get("stations");
            for (Map.Entry<String, Object> station : stations.entrySet()) {
                DataMapDto<RecordDtoImpl> typeMap = new DataMapDto<RecordDtoImpl>();
                LinkedHashMap<String,Object> typesContainer= parseMap(station.getValue());
                LinkedHashMap<String, Object> types = parseMap(typesContainer.get("sdatatypes"));
                for (Map.Entry<String, Object> type : types.entrySet()) {
                    LinkedHashMap<String, List<LinkedHashMap<String,String>>> value = (LinkedHashMap<String, List<LinkedHashMap<String, String>>>) type.getValue();
                    String time = value.get("tmeasurements").get(0).get("mvalidtime");
                    List<RecordDtoImpl> data = new ArrayList<RecordDtoImpl>();
                    SimpleRecordDto e = new SimpleRecordDto();
                    e.setValue(time);
                    data.add(e);
                    typeMap.getBranch().put(type.getKey(),new DataMapDto<RecordDtoImpl>(data));
                }
                dto.getBranch().put(station.getKey(), typeMap);
            }
        }
        return dto;
    }

    private LinkedHashMap<String, Object> parseMap(Object value) {
        if (value instanceof LinkedHashMap)
            return (LinkedHashMap<String, Object>) value;
        return null;
    }
    public List<SimpleRecordDto> getStationData(String station, String type, String latestElaboration) throws ParseException {
        LinkedHashMap<String, Object> data = client.getStationData(station, type, latestElaboration);
        return parseHistoryFromResponse(station,type,data);
    }
    public List<SimpleRecordDto> getStationData(String station, String type) throws ParseException {
        String guessOldestRawData = client.guessOldestRawData(station,type);
        LinkedHashMap<String, Object> data = client.getStationData(station, type, guessOldestRawData);
        List<SimpleRecordDto> parsedData = parseHistoryFromResponse(station,type,data);
        return parsedData;
    }
    private List<SimpleRecordDto> parseHistoryFromResponse(String station, String type, LinkedHashMap<String, Object> stationData) {
        List<SimpleRecordDto> history = new ArrayList<SimpleRecordDto>();
        LinkedHashMap<String, Object> dataSet = (LinkedHashMap<String, Object>) stationData.get("data");
        if (!dataSet.isEmpty()) {
            LinkedHashMap<String,Object> ninjaTree = (LinkedHashMap<String, Object>) dataSet.get("EnvironmentStation");
            LinkedHashMap<String,Object> stationMap = (LinkedHashMap<String, Object>) ((LinkedHashMap<String, Object>) ninjaTree.get("stations")).get(station);
            LinkedHashMap<String,List<LinkedHashMap<String,Object>>> data =  (LinkedHashMap<String, List<LinkedHashMap<String, Object>>>) ((LinkedHashMap<String, Object>) stationMap.get("sdatatypes")).get(type);
            for (LinkedHashMap<String,Object> element:data.get("tmeasurements")) {
                SimpleRecordDto record = new SimpleRecordDto();
                record.setValue(element.get("mvalue"));
                try {
                    record.setTimestamp(client.parseDate(element.get("mvalidtime").toString()).getTime());
                } catch (ParseException e1) {
                    e1.printStackTrace();
                    continue;
                }
                history.add(record);
            };
        }
        return history;
    }
}
