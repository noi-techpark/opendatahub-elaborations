// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.bz.odh.elaborations.services;

import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.time.DateUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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

    private Logger logger = LoggerFactory.getLogger(JobScheduler.class);

    @Autowired
    private ODHParser odhParser;

    @Autowired
    private ElaborationService elaborationService;

    @Autowired
    private ODHWriterClient webClient;

    @Scheduled(cron = "${SCHEDULER_CRON:30 5 * * * *}")
    public void executeAirqualityElaborations() {
        logger.info("Start retrieving data");
        String stationtype = "EnvironmentStation";
        try {
            DataMapDto<RecordDtoImpl> dataMap = getRawDataMap(stationtype);
            logger.info("Create elaboration map with newest elaboration timestamps");
            DataMapDto<RecordDtoImpl> newestElaborationMap = odhParser.createNewestElaborationMap(stationtype);
            logger.info("Start iteration through tree to do elaborations");
            decideWhatToCalculate(dataMap, newestElaborationMap, AN_HOUR_IN_MS);
        } catch (Exception e) {
            logger.warn("Failed to get necessary data from opendatahub. Stopping all elaborations");
            throw e;
        }
        logger.info("Finished pushing elaborations");
    }

    private DataMapDto<RecordDtoImpl> getRawDataMap(String stationtype) {
        DataMapDto<RecordDtoImpl> dataMap = odhParser.createDataMap(stationtype);
        if (!dataMap.getBranch().isEmpty())
            logger.info("Successfully created non empty Raw datatype map");
        else
            logger.info("Got no data to create a Raw datatype map");
        return dataMap;
    }

    private void decideWhatToCalculate(DataMapDto<RecordDtoImpl> rawData,
            DataMapDto<RecordDtoImpl> newestElabData, int minTimePassedSinceLastElaboration) {
        long now = new Date().getTime();
        for (Map.Entry<String, DataMapDto<RecordDtoImpl>> rawStation : rawData.getBranch().entrySet()) {
            String stationId = rawStation.getKey();
            DataMapDto<RecordDtoImpl> rawStationDto = rawStation.getValue();

            for (String dataTypeId : rawStation.getValue().getBranch().keySet()) {
                try {
                    DataMapDto<RecordDtoImpl> elabStationDto = newestElabData.getBranch().get(stationId);
                    
                    long lastElaborationDateUTC = getLastMeasurementTimestamp(elabStationDto, dataTypeId);
                    long lastRawDateUTC = getLastMeasurementTimestamp(rawStationDto, dataTypeId);

                    if (now >= lastElaborationDateUTC + minTimePassedSinceLastElaboration ){
                        startElaboration(stationId, dataTypeId, lastElaborationDateUTC, lastRawDateUTC, now);
                    }
                } catch(Exception e) {
                    logger.error("Something went wrong calculating: " + stationId+"-"+dataTypeId+":"+e.getMessage());
                    e.printStackTrace();
                }
            }
        }
    }

    private long getLastMeasurementTimestamp(
        DataMapDto<RecordDtoImpl> stationDto,
        String dataTypeId ) {

        if (stationDto != null
            && !stationDto.getBranch().isEmpty()
            && stationDto.getBranch().get(dataTypeId) != null
            && !stationDto.getBranch().get(dataTypeId).getData().isEmpty()
        ){
            return stationDto.getBranch().get(dataTypeId).getData().get(0).getTimestamp();
        } else {
            return 0;
        }
    }

    private void startElaboration(String station, String type, long lastElaborationDateUTC, long lastRawDateUTC,
            long now) throws ParseException {
        long elabWindowStart = lastElaborationDateUTC;
        while (elabWindowStart < lastRawDateUTC){
            List<SimpleRecordDto> rawData = odhParser.getRawData(station, type, elabWindowStart);
            if (rawData.isEmpty()){
                elabWindowStart = odhParser.getEndOfInterval(station, type, elabWindowStart, null);
                logger.warn("Unable to get raw data for " + station + ":" + type);
                continue;
            }

            List<SimpleRecordDto> averageElaborations = elaborationService.calcAverage(now, rawData, Calendar.HOUR);

            long endOfRawInterval = getNewestRawTimestamp(rawData);

            if (averageElaborations.isEmpty()) {
                logger.warn("Unable to calculate any data. Maybe not enough data points in interval?");
                if (endOfRawInterval < lastRawDateUTC){
                    // find the next data point, and use that as start. This way we skip empty periods
                    elabWindowStart = odhParser.getEndOfInterval(station, type, endOfRawInterval, null);
                } else {
                    // We've reached the end of of available raw data (loop will terminate)
                    elabWindowStart = endOfRawInterval;
                }
            } else {
                DataMapDto<RecordDtoImpl> dto = new DataMapDto<>();
                dto.addRecords(station, type, averageElaborations);

                logger.debug("Created " + averageElaborations.size() + " elaborations for " + station + ":" + type);
                try {
                    webClient.pushData(dto);
                } catch (Exception ex) {
                    ex.printStackTrace();
                    throw new IllegalStateException("Failed to push data for station:" + station + " and type:" + type);
                }
                logger.debug("Completed sending to odh");

                elabWindowStart = DateUtils
                    .ceiling(new Date(getNewestRawTimestamp(averageElaborations)),
                            Calendar.HOUR)
                    .getTime();
            }
        } 
    }

    private Long getNewestRawTimestamp(List<SimpleRecordDto> rawData) {
        return rawData.get(rawData.size() - 1).getTimestamp();
    }
}
