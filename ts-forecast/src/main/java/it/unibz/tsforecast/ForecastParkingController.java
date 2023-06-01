// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast;

import it.unibz.tsforecast.configuration.TSForecastConfig;
import it.unibz.tsforecast.domain.ParkingForecasts;
import it.unibz.tsforecast.entity.ObservationPeriodicity;
import it.unibz.tsforecast.xml.ForecastXMLDeserializer;

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
@RequestMapping("/lotprediction")
public class ForecastParkingController {
	
	private TSForecastConfig config;
	
	public ForecastParkingController(){
		ApplicationContextLoader l = new ApplicationContextLoader();
		l.load(ForecastParkingController.class, "META-INF/spring/applicationContext.xml");
		this.config = l.getApplicationContext().getBean(TSForecastConfig.class);
	}
	@RequestMapping(headers = "Accept=application/json")
	@ResponseBody
	public ResponseEntity<String> listJson(
			@RequestParam(value = "pid", required = true) String pid,@RequestParam(value="period",required=false)Integer minutes) {
		HttpHeaders headers = new HttpHeaders();
		ForecastXMLDeserializer des = new ForecastXMLDeserializer(this.config);
		ParkingForecasts f;
		if (minutes==null)
			f = des.getForecastsPerParkingLot(ObservationPeriodicity.HALFHOURLY, pid);
		else
			f = des.getForecastsPerParkingLot(ObservationPeriodicity.HALFHOURLY, pid);
		if(f==null ||f.getParkingForecasts()==null || f.getParkingForecasts().size()==0){
			return new ResponseEntity<String>("could not find any parking lot",
					headers, HttpStatus.FORBIDDEN);
		}
		String jsonString = f.parkingForecastsToJSON();
		return new ResponseEntity<String>(jsonString, headers,HttpStatus.OK);
	}
}
