package it.unibz.tsmodel.model.evaluation;
import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ParkingPlace;

import java.util.ArrayList;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import weka.classifiers.timeseries.WekaForecaster;
import weka.classifiers.timeseries.eval.TSEvaluation;
import weka.core.Instances;

/**
 * @author mreinstadler this class is used to evaluate a weka model used for the
 *         accuracy of the predictions
 * 
 */
public class ModelEvaluator {

	private final static Log logger = LogFactory.getLog(ModelEvaluator.class);
	private static double SPLIT_TRAINING_SET = 0.1;

	/**
	 * @param instances
	 *            the single data instances
	 * @param parkingPlace the {@link ParkingPlace} which model is evaluated
	 * @param forecaster
	 *            the forecaster used for weka
	 * @param config the configuration of the application
	 * @return a list of mean errors for each forecast step
	 * @throws Exception
	 */
	public static ArrayList<Float> getMeanErrorsInTime(Instances instances,ParkingPlace parkingPlace,
			WekaForecaster forecaster, TSModelConfig config) {
		ArrayList<Float> meanErrors = null;
		logger.info("Start to evaluate the model of parking lot "+ parkingPlace.getParkingId());
		try {
			TSEvaluation evaluation = new TSEvaluation(instances, SPLIT_TRAINING_SET);
			evaluation.setHorizon(config.getForecastSteps());
			evaluation.setEvaluateOnTestData(config.getEvaluationStrategy().isTestEval());
			evaluation.setEvaluateOnTrainingData(config.getEvaluationStrategy().isTrainingEval());
			evaluation.setForecastFuture(false);
			evaluation.evaluateForecaster(forecaster);
			
		} catch (Exception e) {
			logger.warn("could not evaluate the model of parking lot "+ parkingPlace.getParkingId());
			return new ArrayList<Float>();
		}
		logger.info("Finish to evaluate the model of parking lot "+ parkingPlace.getParkingId());
		return meanErrors;
	}
	
		
	


}
