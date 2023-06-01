// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.forecast;
import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ObservationMetaInfo;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingPlace;
import it.unibz.tsmodel.forecast.domain.ForecastStep;
import it.unibz.tsmodel.forecast.domain.ParkingPrediction;
import it.unibz.tsmodel.forecast.domain.TSPrediction;
import it.unibz.tsmodel.model.ModelBuilder;
import it.unibz.tsmodel.model.TSModel;
import it.unibz.tsmodel.overlay.OverlayAttribute;
import it.unibz.tsmodel.parser.ArffParkingObject;
import it.unibz.tsmodel.parser.TimeSeries;

import java.io.StringReader;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;

import weka.classifiers.evaluation.NumericPrediction;
import weka.classifiers.timeseries.WekaForecaster;
import weka.core.Instances;

/**
 * @author mreinstadler this class makes a previously defined steps of forecasts
 *         (see {@link TSGeneralConfiguration}) and saves them to XML file. This class
 *         runs as cron-job to predict the free slots each hour freshly
 * 
 */
class FullTSForecastGenerator implements TSForecastGenerator {
	private final Log logger = LogFactory.getLog(FullTSForecastGenerator.class);
	@Autowired
	private ModelBuilder tsModelBuilder;
	@Autowired
	private TimeSeries timeSeries;
	@Autowired
	private TSModelConfig config;
	
	
	public FullTSForecastGenerator(){
		
	}
	
	@Override
	public void predictAllFreeSlots(ObservationPeriodicity periodicity) throws Exception {
		logger.info(
				"Start the prediction process by building models and writing predictions to XML ...");
		ArrayList<TSModel> models;
		List<List<NumericPrediction>> wekaforecasts;
		ArrayList<ForecastStep> forecastInstances = new ArrayList<ForecastStep>();
		Instances futureInstances = null;
		ArrayList<ArffParkingObject> arffObjects = timeSeries.generateHistoryArff(periodicity);
		models = tsModelBuilder.buildAllForecastModels(arffObjects, periodicity);
		String futureArff = timeSeries.generateFutureArff(periodicity);
		futureInstances = new Instances(new StringReader(futureArff));
		for (Timestamp futureTimestamp: timeSeries.getFutureDates())
			forecastInstances.add(new ForecastStep(futureTimestamp, 
					getMetaData(timeSeries, futureTimestamp), periodicity));
		logger.info("start forecast and evaluation process...");
		for (TSModel model : models) {
		   
		   /* this may generate errors with evaluationmode=true
		   // Piazza Walther generate an exception. skip it meanwhile!
		   if (model.getParkingPlace().getParkingId() == 103)
		      continue;
		   // Laurin generate an exception. skip it meanwhile!
         if (model.getParkingPlace().getParkingId() == 105)
            continue;
         // Fiera generate an exception. skip it meanwhile!
         if (model.getParkingPlace().getParkingId() == 116)
            continue;
         */
		   
			WekaForecaster f = model.getForecastModel();
			try{
			wekaforecasts = f.forecast(config.getForecastSteps(),
					futureInstances, System.out);
			}catch(Exception ex){
				continue;
			}
			int a = 0;
			for (ForecastStep forecastStep : forecastInstances) {
				int predictedFreeSlots = new Double(wekaforecasts.get(a).get(0)
						.predicted()).intValue();
				double lowerConfInterval = predictedFreeSlots;
				double upperConfInterval = predictedFreeSlots;
				if(config.isModelEvaluation()){
					
					double d1 = wekaforecasts.get(a).get(0).predictionIntervals()[0][0];
					if(!Double.valueOf(NumericPrediction.MISSING_VALUE).equals(d1))
						lowerConfInterval= d1;
					double d2= wekaforecasts.get(a).get(0).predictionIntervals()[0][1];
					if(!Double.valueOf(NumericPrediction.MISSING_VALUE).equals(d2))
						upperConfInterval= d2;
				}
				TSPrediction pr = new TSPrediction(predictedFreeSlots, upperConfInterval, lowerConfInterval);
				ParkingPlace pl = model.getParkingPlace();
				ParkingPrediction forecast = new ParkingPrediction(pl, pr);
				forecastStep.addOneParkingPrediction(forecast);
				a++;
			}

		}
		logger.info("forecast and evaluation process completed");
		ForecastXMLSerializer xmlSerializer = new ForecastXMLSerializer();
		xmlSerializer.serializeXML(forecastInstances, periodicity, config);

		logger.info("Prediction process is finished and saved");
	}
	
	/**
	 * @param timeseries the {@link TimeSeries}
	 * @param timestamp the timestamp of the forecast
	 * @return the list of {@link ObservationMetaInfo} for the given hour
	 */
	private ArrayList<ObservationMetaInfo> getMetaData(TimeSeries timeseries, Timestamp timestamp){
		ArrayList<ObservationMetaInfo> metaInformations = new ArrayList<ObservationMetaInfo>();
		for(OverlayAttribute overlayAttr : timeseries.getOverlayAttributes().getOverlayAttributes())
			metaInformations.add(overlayAttr.getMetaInformation(timestamp));
		return metaInformations;
	}
	
	
	/**
	 * @return the tsModelBuilder
	 */
	public ModelBuilder getTsModelBuilder() {
		return tsModelBuilder;
	}

	/**
	 * @param tsModelBuilder the tsModelBuilder to set
	 */
	public void setTsModelBuilder(ModelBuilder tsModelBuilder) {
		this.tsModelBuilder = tsModelBuilder;
	}

	/**
	 * @return the timeSeries
	 */
	public TimeSeries getTimeSeries() {
		return timeSeries;
	}

	/**
	 * @param timeSeries the timeSeries to set
	 */
	public void setTimeSeries(TimeSeries timeSeries) {
		this.timeSeries = timeSeries;
	}

}
