package it.unibz.tsmodel.model;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.parser.ArffParkingObject;

import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;

import weka.classifiers.timeseries.WekaForecaster;
import weka.core.Instances;

/**
 * This class builds or rebuilds the models for the parking places. Based on
 * these models the prediction can be made by the ForeCaster
 * 
 * @author mreinstadler
 * 
 */
public class TSModelBuilder implements
		ModelBuilder {
	
	
	private final Log logger = LogFactory.getLog(TSModelBuilder.class);
	@Autowired
	private TSModelConfig config;



	/**
	 * Constructs the modelbuilder
	 */
	public TSModelBuilder(){
		
	}
	
	

	
	@Override
	public ArrayList<TSModel> buildAllForecastModels(
			ArrayList<ArffParkingObject> arffs, ObservationPeriodicity periodicity) {

		logger.info("Start building all the models...");
		ArrayList<TSModel> models = new ArrayList<TSModel>();
		for (ArffParkingObject arff : arffs) {
			models.add(buildSingleModel(arff, periodicity));
		}
		logger.info("End building all the models");
		return models;

	}

	@Override
	public TSModel buildSingleModel(ArffParkingObject arffObject, ObservationPeriodicity periodicity) {
		logger.info("Start building model with overlay data for parking place "
						+ arffObject.getParkingplace().getParkingId());
		WekaForecaster forecaster = null;
		Instances instances = null;
		try {
			instances = new Instances(new StringReader(
					arffObject.getArffString()));
			forecaster = new WekaForecaster();
			TSModelConfigurator.configureForecaster(forecaster,arffObject.getOverlay(), periodicity, this.config);
			forecaster.buildForecaster(instances, System.out);
			forecaster.primeForecaster(instances);
			logger.info(
					"End building model with overlay data for parkingplace "
							+ arffObject.getParkingplace().getParkingId());
		} catch (IOException e) {
			logger.warn(
					"could not build single model of parking place"
							+ arffObject.getParkingplace().getParkingId());
		} catch (Exception e) {
			logger.warn(
					"could not build single model of parking place"
							+ arffObject.getParkingplace().getParkingId());
		}
		return new TSModel(forecaster, arffObject.getParkingplace(), instances);
	}
	
	/**
	 * @return the config
	 */
	public TSModelConfig getConfig() {
		return config;
	}




	/**
	 * @param config the config to set
	 */
	public void setConfig(TSModelConfig config) {
		this.config = config;
	}


}
