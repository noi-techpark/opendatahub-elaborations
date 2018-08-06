package it.unibz.tsmodel.parser.filter;

import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;

import java.util.List;

public interface TSInterpolationFilter {
	
	/**
	 * this filters the faulty observation instances by applying one of the available methods
	 * @param parkingObservations the {@link ParkingObservation} to buid up the time-series
	 * @param periodicity the {@link ObservationPeriodicity} of the {@link ParkingObservation}
	 */
	public void filterTimeseries(List<ParkingObservation> parkingObservations, 
			ObservationPeriodicity periodicity);

}
