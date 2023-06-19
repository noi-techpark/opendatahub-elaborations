// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.bz.odh.elaborations.services;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;

import javax.annotation.Resource;

import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Lazy
@Component
public class ODHReaderClient{

    private static final String DATA_ORIGIN = "a22-algorab";
	private static final long A_DAY = 3600*24*1000l;
    private static final long A_MONTH = A_DAY*31;
    private static final String DEFAULT_OLDEST_DATA_ELABORATION = "2020-01-01T00:00:00.000+0000";
    private DateFormat dateFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ");
    private DateFormat responseDateFormatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSSZ");

    @Resource(name = "ninja")
    protected WebClient ninja;

    public LinkedHashMap<String, Object> getStationData(String station,String type, Date from, Date to, Integer limit, String dataOrigin) {
        return getRawData(station, type, dateFormatter.format(from), dateFormatter.format(to), limit, dataOrigin);
    }

    public LinkedHashMap getRawData(String station,String type,String from, String to, Integer limit, String dataOrigin) {
        return ninja.get().uri("/v2/tree/EnvironmentStation/" + type + "/" + from + "/" +  to
                        + "?limit=" + limit + "&where=sactive.eq.true,sorigin.eq." + (dataOrigin != null ? dataOrigin : DATA_ORIGIN) + ",scode.eq."+station+",mperiod.eq.60&select=tmeasurements")
                .retrieve().bodyToFlux(LinkedHashMap.class).blockLast();
    }

    public LinkedHashMap getLatestNinjaTree() {
        LinkedHashMap blockLast = ninja.get()
			        .uri("/v2/tree/EnvironmentStation/*/latest?limit=-1&where=sactive.eq.true,sorigin.eq." + DATA_ORIGIN
							+ ",mperiod.eq.60&select=mvalidtime")
			        .retrieve().bodyToFlux(LinkedHashMap.class).blockLast();
        if (blockLast==null || ((LinkedHashMap<String, Object>) blockLast.get("data")).isEmpty())
            throw new IllegalStateException("Opendatahub returned no valid raw data to do elaborations on");
        return blockLast;
    }

    public LinkedHashMap createNewestElaborationMap() {
        return ninja.get().uri("/v2/tree/EnvironmentStation/*/latest?limit=-1&where=sactive.eq.true,sorigin.eq." + DATA_ORIGIN
				+ ",mperiod.eq.3600&select=mvalidtime")
                .retrieve().bodyToFlux(LinkedHashMap.class).blockLast();
    }

    public LinkedHashMap<String,Object> getRawData(String station, String type, Long lastElaborationDateinMS) {
        long aMonthLaterAsMS = lastElaborationDateinMS + A_MONTH;
        String lastElaborationDateString = dateFormatter.format(lastElaborationDateinMS);
        String aMonthLaterString = dateFormatter.format(new Date(aMonthLaterAsMS));
        return getRawData(station, type, lastElaborationDateString, aMonthLaterString,-1, null);
    }

    public Long guessOldestRawData(String station, String type) {
        try {
            Date oldest = dateFormatter.parse(DEFAULT_OLDEST_DATA_ELABORATION);
            return recursiveOldestDateRetrieval(station, type, oldest,new Date(oldest.getTime() + A_MONTH));
        } catch (ParseException e) {
            e.printStackTrace();
            throw new IllegalStateException(e);
        }
    }

    private Long recursiveOldestDateRetrieval(String station, String type, Date from, Date to) throws ParseException {
        if (from.after(new Date()))
            throw new IllegalStateException("This should not happen since only existing station types should be called");
        LinkedHashMap<String, Object> stationData = getStationData(station, type, from,to,-1, null);
        String oldestRecordDateString = parseOldestRecordFromResponse(station,type,stationData);
        return oldestRecordDateString != null ? parseDate(oldestRecordDateString).getTime(): recursiveOldestDateRetrieval(station, type,to,new Date(to.getTime() + A_MONTH));
    }

    private String parseOldestRecordFromResponse(String station, String type, LinkedHashMap<String, Object> stationData) {
        String oldestRecordDate = null;
        LinkedHashMap<String, Object> dataSet = (LinkedHashMap<String, Object>) stationData.get("data");
        if (!dataSet.isEmpty()) {
            LinkedHashMap<String,Object> ninjaTree = (LinkedHashMap<String, Object>) dataSet.get("EnvironmentStation");
            LinkedHashMap<String,Object> stationMap = (LinkedHashMap<String, Object>) ((LinkedHashMap<String, Object>) ninjaTree.get("stations")).get(station);
            LinkedHashMap<String,List<LinkedHashMap<String,String>>> data =  (LinkedHashMap<String, List<LinkedHashMap<String, String>>>) ((LinkedHashMap<String, Object>) stationMap.get("sdatatypes")).get(type);
            return data.get("tmeasurements").get(0).get("mvalidtime");
        }
        return oldestRecordDate;
    }

    public Date parseDate(String date) throws ParseException {
        return responseDateFormatter.parse(date);
    }

	public LinkedHashMap<String, Object> getEndOfEmptyInterval(String station, String type, Long lastRawData, String dataOrigin) {
		Date from = new Date(lastRawData+1);
		Date to = new Date(lastRawData + 1000l*3600l*24l*365l*100l);
		return getStationData(station, type, from, to, 1, dataOrigin);
	}
}
