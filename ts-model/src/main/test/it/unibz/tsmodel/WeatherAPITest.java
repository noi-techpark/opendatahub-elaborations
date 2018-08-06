package it.unibz.tsmodel;

import java.util.Calendar;
import static org.junit.Assert.*;
import java.util.List;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.MeteoObservation;
import it.unibz.tsmodel.overlay.weather.IntegreenWeatherReader;
import it.unibz.tsmodel.overlay.weather.WeatherReader;

import org.junit.Test;

public class WeatherAPITest {

	@Test
	public void testIntegreenPredictions() {
		Calendar now = Calendar.getInstance();
		now.set(Calendar.DAY_OF_MONTH, 25);
		WeatherReader reader = new IntegreenWeatherReader();
		TSModelConfig config = new TSModelConfig();
		List<MeteoObservation> weatherObservations = reader.getStoricalWeatherObservations(now, config);
		assertNotNull(weatherObservations);
		assertTrue(!weatherObservations.isEmpty());
		for (MeteoObservation ob:weatherObservations)
			System.out.println("\""+ob.getTimestamp()+"\" = "+ob.getObservedValue());
	}

}
