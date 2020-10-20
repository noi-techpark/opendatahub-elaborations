package it.bz.odh.elaborations;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;

import java.text.DateFormat;
import java.util.Date;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;

import it.bz.odh.elaborations.services.ODHReaderClient;
import it.bz.odh.elaborations.services.ResponseMapping;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations = { "classpath:/META-INF/spring/applicationContext*.xml" })
@WebAppConfiguration
public class ODHIT{

    @Autowired
    private ODHReaderClient client;
    
    private DateFormat dateFormatter = DateFormat.getDateInstance();
    @Test
    public void testFetchStationId() {
        ResponseMapping responseMapping = client.getActiveStationIds();
        List<Object> values = (List<Object>) responseMapping.get("data");
        assertNotNull(values);
        assertFalse(values.isEmpty());
    }
    @Test
    public void testFetchStationData() {
        Date now = new Date();
        Date yesterday = new Date(now.getTime()-24*60*60*1000*31);
        ResponseMapping responseMapping = client.getStationData(yesterday, now);
        List<Object> values = (List<Object>) responseMapping.get("data");
        assertNotNull(values);
        assertFalse(values.isEmpty());
    }
}
