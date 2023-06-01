// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.forecast;

import java.util.Calendar;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;
import org.springframework.stereotype.Service;

import io.sentry.Sentry;
import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.overlay.weather.MeteoUtil;

/**
 * @author mreinstadler this class starts the cron (each hour) and creates all
 *         the forecasts for the various parking lots
 * 
 */
@Service
public class ForecastCron {
	private final Log logger = LogFactory.getLog(ForecastCron.class);
	@Autowired
	private FullTSForecastGenerator tsForecaster;
	@Autowired
	private TSModelConfig config;
	@Autowired
	private MeteoUtil meteoUtil;
	
	//@Autowired ThreadPoolTaskExecutor executor;
   @Autowired ThreadPoolTaskScheduler scheduler;

	/**
	 * generates all the forecasts for the parking lots this runs as cron job
	 * each hour
	 */
	
	// For dev better to have a fixedDelay that make the method start immediately
   // @Scheduled(fixedDelay=600000)
	@Scheduled(cron= "0 */30 * * * *")
	public void createForecasts() {
	   try
	   {
	      Sentry.capture("ForecastCron.createForecasts");
   	   Calendar now = Calendar.getInstance();
   		logger.info("Update Meteo Data");
   		meteoUtil.getPastObservations();
   		logger.info("Start the forecast cron at " + config.getDateformatInUse().format(now.getTime()));
   		logger.info("Start the forecast cron...");
   		logger.info("application settings are: "+System.getProperty("line.separator")+ this.config.toString());
   		if (config.isAllObservationPeriodicity()) {
   			for (ObservationPeriodicity period : ObservationPeriodicity
   					.values()) {
   				try {
   					tsForecaster.predictAllFreeSlots(period);
   				} catch (Exception e) {
   				   Sentry.capture(e);
   					e.printStackTrace();
   				}
   			}
   		}
   		else{
   			try {
   				tsForecaster.predictAllFreeSlots(ObservationPeriodicity.HALFHOURLY);
   			} catch (Exception e) {
   			   Sentry.capture(e);
   				e.printStackTrace();
   			}
   		}
   		logger.info("Forecast cron completed");
	   }
	   catch (Exception exxx)
	   {
	      Sentry.capture(exxx);
	   }
	}
	
	public ThreadPoolTaskScheduler getScheduler()
   {
      return scheduler;
   }
}
