package it.bz.odh.elaborations;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;

import java.util.LinkedHashMap;
import java.util.Map.Entry;
import java.util.Set;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;

import it.bz.idm.bdp.dto.DataMapDto;
import it.bz.idm.bdp.dto.RecordDtoImpl;
import it.bz.odh.elaborations.services.JobScheduler;
import it.bz.odh.elaborations.services.ODHParser;
import it.bz.odh.elaborations.services.ODHReaderClient;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations = { "classpath:/META-INF/spring/applicationContext*.xml" })
@WebAppConfiguration
public class ODHIT{

    @Autowired
    private ODHReaderClient client;
    
    @Autowired
    private ODHParser parser;

    @Autowired
    private JobScheduler scheduler;
    
    @Test
    public void testFetchStationId() {
        Set<Entry<String, Object>> latestNinjaTree = client.getLatestNinjaTree().entrySet();
        assertNotNull(latestNinjaTree);
        assertFalse(latestNinjaTree.isEmpty());
    }
    @Test
    public void testFetchStationData() {
        String from = "2020-10-05T23:58:59.999";
        String to = "2020-10-05T23:59:59.999";
        LinkedHashMap<String, Object> responseMapping = client.getStationData("","",from,to);
        LinkedHashMap<String, Object>values = (LinkedHashMap<String, Object>) responseMapping.get("data");
        assertNotNull(values);
        assertFalse(values.isEmpty());
    }
    
    @Test
    public void testCreateDataMap() {
        DataMapDto<RecordDtoImpl> createDataMap = parser.createDataMap("EnvironmentStation");
        System.out.println(createDataMap.toString());
    }
    @Test
    public void testCreateElaborationMap() {
        DataMapDto<RecordDtoImpl> dataMap = parser.createNewestElaborationMap("EnvironmentStation");
        System.out.println(dataMap.toString());
    }
    
    @Test
    public void testStartElaborations() {
       scheduler.executeAirqualityElaborations();
    }
}
