package it.unibz.tsmodel.model;

import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.parser.ArffParkingObject;

import java.util.ArrayList;

/**
 * @author mreinstadler this interface must be implemented by each timeseries
 *         model builder (for univariate or multivariate timeseries)
 * 
 */
public interface ModelBuilder {
	/**
	 * this function builds or rebuilds all the prediction models of the single
	 * parking places.
	 * 
	 * @param arffs
	 *            the {@link ArffParkingObject} to build the {@link TSModel}
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @return the list of {@link TSModel} for the parking places
	 */
	public ArrayList<TSModel> buildAllForecastModels(
			ArrayList<ArffParkingObject> arffs, ObservationPeriodicity periodicity);

	/**
	 * creates a new ForecastModel when the current one is not up-to-date
	 * @param arff
	 *            the {@link ArffParkingObject} to build the model on
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @return the new {@link TSModel} of this parking place
	 * @throws Exception
	 */
	public TSModel buildSingleModel(ArffParkingObject arff, ObservationPeriodicity periodicity);

}
