package com.opendatahub.rest;

import java.util.Arrays;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.client.RestTemplate;

import com.opendatahub.dto.Flights;

public class FlightsRest {

	private static final String URL_GET_FLIGHTS = "https://mobility.api.opendatahub.com/v2/flat,node/Flight?limit=-1";
	private static final Logger LOG = LoggerFactory.getLogger(FlightsRest.class);

	@RequestMapping(value = "/getFlights", method = RequestMethod.POST)
	@ResponseBody
	public static Flights getFlights(RestTemplate restTemplate) {
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		headers.setAccept(Arrays.asList(MediaType.ALL)); /* Collections.singletonList(MediaType.APPLICATION_JSON) */
		ResponseEntity<Flights> response = restTemplate.getForEntity(URL_GET_FLIGHTS, Flights.class);
		if (response.getStatusCode() == HttpStatus.OK) {
			LOG.info("Request Successful {}", URL_GET_FLIGHTS);
			LOG.debug("" + response.getBody());
			return (response.getBody());

		} else {
			LOG.info("Request Failed {}", URL_GET_FLIGHTS);
			LOG.debug("" + response.getStatusCode());
		}
		return (null);

	}
}
