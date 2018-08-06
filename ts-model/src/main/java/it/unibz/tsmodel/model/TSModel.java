package it.unibz.tsmodel.model;

import it.unibz.tsmodel.domain.ParkingPlace;
import it.unibz.tsmodel.model.strategy.EvaluationStrategy;
import weka.classifiers.timeseries.WekaForecaster;
import weka.core.Instance;
import weka.core.Instances;

/**
 * @author mreinstadler This class represents a Model used for the forecasting
 *         process. The model includes one {@link ParkingPlace}, a {@link WekaForecaster}, 
 *         an object of {@link Instances}, a {@link ModelEvaluation} and finally an 
 *         {@link EvaluationStrategy} used to evaluate the model
 */
public class TSModel {
	private WekaForecaster forecastModel;
	private ParkingPlace parkingPlace;
	private Instances instances;

	/**
	 * creates a new ForecastModel with the given input
	 * @param forecaster
	 *            the {@link WekaForecaster}, which builded the model
	 * @param place
	 *            {@link ParkingPlace} where the model was build on
	 * @param instances the {@link Instances} used to build the model
	 * @param config the configuration of the model
	 */
	public TSModel(WekaForecaster forecaster, ParkingPlace place,
			Instances instances) {
		this.forecastModel = forecaster;
		this.parkingPlace = place;
		this.instances = instances;

	}

	/**
	 * @return the model of the forecast as {@link WekaForecaster}
	 */
	public WekaForecaster getForecastModel() {
		return forecastModel;
	}

	/**
	 * @return the {@link ParkingPlace} the model was build on
	 */
	public ParkingPlace getParkingPlace() {
		return this.parkingPlace;
	}


	/**
	 * @return the {@link Instances} used to build the model
	 */
	public Instances getInstances() {
		return instances;
	}

	/**
	 * @param instance
	 *            the {@link Instance} to be added to the set of instances used to build
	 *            the model
	 */
	public void addInstances(Instance instance) {
		this.instances.add(instance);
	}

}
