// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast;
import it.unibz.tsforecast.configuration.TSForecastConfig;
import it.unibz.tsforecast.domain.ForecastStep;
import it.unibz.tsforecast.entity.ObservationPeriodicity;
import it.unibz.tsforecast.xml.ForecastXMLDeserializer;

import java.util.Calendar;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

/**
 * Handles requests for the application home page.
 */
@Controller
@RequestMapping("/predictions")
public class ForecastStepController {
	 
private TSForecastConfig config;
	
	public ForecastStepController() {
		ApplicationContextLoader l = new ApplicationContextLoader();
		l.load(ForecastParkingController.class, "META-INF/spring/applicationContext.xml");
		this.config = l.getApplicationContext().getBean(TSForecastConfig.class);
	}
	
	
	@RequestMapping(headers = "Accept=application/json")
	@ResponseBody
	public ResponseEntity<String> listJson(
			@RequestParam(value = "minutes", required = true) Integer minutesInFuture) {
		
		HttpHeaders headers = new HttpHeaders();
		headers.add("Content-Type", "application/json; charset=utf-8");
		if(minutesInFuture==null){
			return new ResponseEntity<String>("please specify a date in future",
					headers, HttpStatus.FORBIDDEN);
		}
		if(minutesInFuture<1){
			return new ResponseEntity<String>("negative forecasts are not accepted",
					headers, HttpStatus.FORBIDDEN);
		}
		String jsonString = constructJSON(minutesInFuture);
		if(jsonString==null){
			return new ResponseEntity<String>("no forecast possible for the specified date",
					headers, HttpStatus.METHOD_FAILURE);
		}
		return new ResponseEntity<String>(jsonString, HttpStatus.OK);
	}
	/**
	 * helper method that constructs the JSON string
	 * @param hoursInFuture the desired date of forecast
	 * @return the resulting JSON string
	 */
	private String constructJSON(int minutes) {
		Calendar forecastDate = Calendar.getInstance();
		forecastDate.add(Calendar.MINUTE, minutes);
		ForecastXMLDeserializer foreCaster = new ForecastXMLDeserializer(this.config);
		String jsonString = null;
		ForecastStep step = foreCaster.getForecastStep(ObservationPeriodicity.HALFHOURLY, forecastDate);
			if(step!=null)
				jsonString = step.forecaststepToJSON(); 
		return jsonString;
	
	}
	
}
