package it.bz.odh.elaborations;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;

import it.bz.odh.elaborations.services.ResponseMapper;
import it.bz.odh.elaborations.services.ResponseMapping;

@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations = { "classpath:/META-INF/spring/applicationContext*.xml" })
@WebAppConfiguration
public class UtilityTest{

    @Test
    public void testDataParsing() {
        ResponseMapping mapping = new ResponseMapping();
        ResponseMapper.getStationIdsAsList(mapping);
    }
}
