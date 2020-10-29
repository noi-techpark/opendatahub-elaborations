package it.bz.odh.elaborations.services;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;

import javax.annotation.Resource;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
@Lazy
@Component
public class ODHReaderClient{
    
    private static final long A_DAY = 3600*24*1000l;
    private static final long A_MONTH = A_DAY*31;
    @Resource(name = "ninja")
    protected WebClient ninja;
    private DateFormat dateFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSZ");
    private DateFormat responseDateFormatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSSZ");
    
    private String oldestRawDataElab = "2020-01-01T00:00:00.000+0000";
    
    public LinkedHashMap<String, Object> getStationData(String station,String type, Date from, Date to) {
        return getStationData(station, type, dateFormatter.format(from), dateFormatter.format(to));
    }
    public LinkedHashMap getStationData(String station,String type,String from, String to) {
        return ninja.get().uri("/v2/tree/EnvironmentStation/" + type + "/" + from + "/" +  to
                        + "?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab,scode.eq."+station+"&select=tmeasurements")
                .retrieve().bodyToFlux(LinkedHashMap.class).blockLast();
    }
    public LinkedHashMap getLatestNinjaTree() {
        return ninja.get()
                .uri("/v2/tree/EnvironmentStation/*/latest?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab,mperiod.eq.600&select=mvalidtime")
                .retrieve().bodyToFlux(LinkedHashMap.class).blockLast();
    }
    public LinkedHashMap createNewestElaborationMap() {
        return ninja.get().uri("/v2/tree/EnvironmentStation/*/latest?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab,mperiod.eq.3600&select=mvalidtime")
                .retrieve().bodyToFlux(LinkedHashMap.class).blockLast();
    }
    public LinkedHashMap<String,Object> getStationData(String station, String type, Long lastElaborationDateString) throws ParseException {
        long from = lastElaborationDateString;
        long to = from + A_MONTH;
        String currentDate = dateFormatter.format(from);
        String later = dateFormatter.format(new Date(to));
        return getStationData(station, type, currentDate, later);
    }
    public Long guessOldestRawData(String station, String type) {
        try {
            Date oldest = dateFormatter.parse(oldestRawDataElab);
            return recursiveOldestDateRetrieval(station, type, oldest,new Date(oldest.getTime() + A_MONTH));
        } catch (ParseException e) {
            e.printStackTrace();
            throw new IllegalStateException(e);
        }        
    }
    private Long recursiveOldestDateRetrieval(String station, String type, Date from, Date to) throws ParseException {
        if (from.after(new Date()))
            throw new IllegalStateException("This should not happen since only existing station types should be called");
        LinkedHashMap<String, Object> stationData = getStationData(station, type, from,to);
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
    
}
