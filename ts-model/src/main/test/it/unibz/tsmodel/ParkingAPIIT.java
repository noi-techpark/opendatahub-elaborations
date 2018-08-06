package it.unibz.tsmodel;

import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.AbstractJUnit4SpringContextTests;

import it.unibz.tsmodel.forecast.ForecastCron;
@ContextConfiguration(locations = { "classpath:/META-INF/spring/applicationContext.xml" })
public class ParkingAPITest extends AbstractJUnit4SpringContextTests{

	@Autowired
	private ForecastCron cron;
	@Test
	public void testParkingObservations() {
		cron.createForecasts();
	}

}
