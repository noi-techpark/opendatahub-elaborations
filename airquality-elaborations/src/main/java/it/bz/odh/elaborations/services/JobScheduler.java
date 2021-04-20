package it.bz.odh.elaborations.services;

import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.time.DateUtils;
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

	private void decideWhatToCalculate(DataMapDto<RecordDtoImpl> dataMap,
			DataMapDto<RecordDtoImpl> newestElaborationMap, int minTimePassedSinceLastElaboration) {
		Long now = new Date().getTime();
		for (Map.Entry<String, DataMapDto<RecordDtoImpl>> stationMapEntry : dataMap.getBranch().entrySet()) {
			for (Map.Entry<String, DataMapDto<RecordDtoImpl>> typeMapEntry : stationMapEntry.getValue().getBranch()
					.entrySet()) {
				try {
					List<RecordDtoImpl> data = new ArrayList<RecordDtoImpl>();
					DataMapDto<RecordDtoImpl> elaborationTypeMap = newestElaborationMap.getBranch()
							.get(stationMapEntry.getKey());
					if (!newestElaborationMap.getBranch().isEmpty() && elaborationTypeMap != null
							&& !elaborationTypeMap.getBranch().isEmpty()
							&& elaborationTypeMap.getBranch().get(typeMapEntry.getKey()) != null
							&& !elaborationTypeMap.getBranch().get(typeMapEntry.getKey()).getData().isEmpty())
						data = elaborationTypeMap.getBranch().get(typeMapEntry.getKey()).getData();

					List<RecordDtoImpl> rawData = dataMap.getBranch().get(stationMapEntry.getKey()).getBranch()
							.get(typeMapEntry.getKey()).getData();
					Long lastElaborationDateUTC = !data.isEmpty() ? data.get(0).getTimestamp() : null;
					Long lastRawDateUTC = rawData.get(0).getTimestamp();
					if (lastElaborationDateUTC == null || now - minTimePassedSinceLastElaboration >= lastElaborationDateUTC) // start
						startElaboration(stationMapEntry.getKey(), typeMapEntry.getKey(), lastElaborationDateUTC,
								lastRawDateUTC, now);
				}catch(Exception e) {
					logger.error("Something went wrong calculating: " + stationMapEntry.getKey()+"-"+typeMapEntry.getKey()+":"+e.getMessage());
					e.printStackTrace();
					continue;
				}
			}
		}
	}

	private void startElaboration(String station, String type, Long lastElaborationDateUTC, Long lastRawDateUTC,
			Long now) throws ParseException {
		List<SimpleRecordDto> stationData = null;
		if (lastElaborationDateUTC != null)
			stationData = odhParser.getRawData(station, type, lastElaborationDateUTC);
		else
			stationData = odhParser.getRawData(station, type);
		if (stationData.size() < ElaborationService.MIN_AMOUNT_OF_DATA_POINTS && lastElaborationDateUTC != null) {
			Long lastRawData = stationData.isEmpty()?lastElaborationDateUTC:stationData.get(stationData.size()-1).getTimestamp();
			Long endOfNoDataInterval = odhParser.getEndOfInterval(station, type, lastRawData, null);
			if (endOfNoDataInterval != null)
				stationData = odhParser.getRawData(station, type, endOfNoDataInterval);
		}
		if (stationData.isEmpty())
			throw new IllegalStateException("Unable to get raw data for " + station + ":" + type);
		List<SimpleRecordDto> averageElaborations = elaborationService.calcAverage(now, stationData, Calendar.HOUR);
		if (averageElaborations.isEmpty())
			throw new IllegalStateException("Unable to calculate any data");

		DataMapDto<RecordDtoImpl> dto = new DataMapDto<RecordDtoImpl>();
		dto.addRecords(station, type, averageElaborations);

		logger.debug("Created " + averageElaborations.size() + " elaborations for " + station + ":" + type);
		try {
			webClient.pushData(dto);
		} catch (Exception ex) {
			ex.printStackTrace();
			throw new IllegalStateException("Failed to push data for station:" + station + " and type:" + type);
		}
		logger.debug("Completed sending to odh");

		Long newOldestElaboration = DateUtils
				.ceiling(new Date(averageElaborations.get(averageElaborations.size() - 1).getTimestamp()),
						Calendar.HOUR)
				.getTime();
		if (newOldestElaboration <= lastRawDateUTC)
			startElaboration(station, type, newOldestElaboration, lastRawDateUTC, now);
	}
}
