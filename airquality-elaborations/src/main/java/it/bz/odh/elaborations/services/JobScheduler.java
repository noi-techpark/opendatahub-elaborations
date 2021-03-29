package it.bz.odh.elaborations.services;

import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang.time.DateUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import it.bz.idm.bdp.dto.DataMapDto;
import it.bz.idm.bdp.dto.RecordDtoImpl;
import it.bz.idm.bdp.dto.SimpleRecordDto;

@Service
@EnableScheduling
public class JobScheduler {

    private static final int AN_HOUR_IN_MS = 3600*1000;

	private Logger logger = LogManager.getLogger(JobScheduler.class);

    @Autowired
    private ODHParser odhParser;

    @Autowired
    private ElaborationService elaborationService;

    @Autowired
    private ODHWriterClient webClient;

    @Scheduled(cron = "0 0 * * * *")
    public void executeAirqualityElaborations() {
        logger.info("Start retrieving data");
        String stationtype = "EnvironmentStation";
        DataMapDto<RecordDtoImpl> dataMap = getRawDataMap(stationtype);
        logger.info("Create elaboration map with newest elaboration timestamps");
        DataMapDto<RecordDtoImpl> newestElaborationMap = odhParser.createNewestElaborationMap(stationtype);
        logger.info("Start iteration through tree to do elaborations");
		decideWhatToCalculate(dataMap, newestElaborationMap, AN_HOUR_IN_MS);
    }
// TODO fix before reenable
//    @Scheduled(cron = "10 */5 * * * *")
    private void executeParkingElaborations() {
	    String stationtype = "ParkingStation";
        logger.info("Start parking elaborations");
        DataMapDto<RecordDtoImpl> dataMap = getRawDataMap(stationtype);
        logger.info("Create elaboration map with newest elaboration timestamps");
        DataMapDto<RecordDtoImpl> newestElaborationMap = odhParser.createNewestElaborationMap(stationtype);
        logger.info("Start iteration through tree to do elaborations");
        decideWhatToCalculate(dataMap, newestElaborationMap, 4*60*1000);
    }

	private DataMapDto<RecordDtoImpl> getRawDataMap(String stationtype) {
		DataMapDto<RecordDtoImpl> dataMap = odhParser.createDataMap(stationtype);
        if (!dataMap.getBranch().isEmpty())
            logger.info("Successfully created non empty Raw datatype map");
        else
            logger.info("Got no data to create a Raw datatype map");
        return dataMap;
	}

	private void decideWhatToCalculate(DataMapDto<RecordDtoImpl> dataMap, DataMapDto<RecordDtoImpl> newestElaborationMap, int minTimePassedSinceLastElaboration) {
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
                if (lastElaborationDateUTC == null || lastRawDateUTC - minTimePassedSinceLastElaboration > lastElaborationDateUTC)  //start elaborations only if there is new data of minTimePassedSinceLastElaboration
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
            logger.info("Create elaboration map with newest elaboration timestamps");
            if (!stationData.isEmpty()) {
                List<SimpleRecordDto> averageElaborations = elaborationService.calcAverage(stationData,Calendar.HOUR);
                if (!averageElaborations.isEmpty()) {
                    DataMapDto<RecordDtoImpl> dto = new DataMapDto<RecordDtoImpl>();
                    dto.addRecords(station, type, averageElaborations);
                    logger.debug("Created "+averageElaborations.size()+" elaborations for "+station+":"+type);
                    webClient.pushData(dto);
                    logger.debug("Completed sending to odh");
                    Long newOldestElaboration = DateUtils.ceiling(new Date(averageElaborations.get(averageElaborations.size()-1).getTimestamp()),Calendar.HOUR).getTime();
                    if (newOldestElaboration <= lastRawDateUTC)
                        startElaboration(station, type, newOldestElaboration, lastRawDateUTC);
                }
            }else {
                logger.debug("Unable to get raw data for "+station+":"+type);
            }
        } catch (ParseException e) {
            e.printStackTrace();
        }
    }
}
