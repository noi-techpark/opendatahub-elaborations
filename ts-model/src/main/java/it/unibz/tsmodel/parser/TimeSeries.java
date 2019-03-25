package it.unibz.tsmodel.parser;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.beans.factory.annotation.Autowired;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.domain.ParkingPlace;
import it.unibz.tsmodel.overlay.OverlayAttributes;
import it.unibz.tsmodel.parser.filter.TSInterpolationFilter;
import it.unibz.tsmodel.parser.tis.ParkingUtil;

/**
 * @author mreinstadler this class is used to generate arff strings for the weka
 *         input. For further information on arff strings see the weka
 *         documentation on http://weka.wikispaces.com/ARFF
 *
 */
public class TimeSeries {

	private ArrayList<Timestamp> futureDates= null;
	private final Log logger = LogFactory.getLog(TimeSeries.class);
	@Autowired
	private TSModelConfig config;
	@Autowired
	OverlayAttributes overlayAttributes;
	@Autowired
	private ParkingUtil parkingUtil;



	/**
	 * initializes the {@link TimeSeries}
	 */
	public TimeSeries() {
	}


	/**
	 * this method creates history arff strings in the following way:
	 * 1) Looks for parking lots
	 * 2) Creates for each lots all the observations from db
	 * 3) checks the TIS webservice if new observations are available and persists them
	 * 4) Filters the observations if required (see {@link ObservationPeriodicity}) for time-spans
	 * 5) Filters the observations for faulty data
	 * 6) creates for each parking place the arff string
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @return the list of {@link ArffParkingObject}, one for each parking
	 *         place. If no objects are available, an empty list is returned
	 */
	public ArrayList<ArffParkingObject> generateHistoryArff(ObservationPeriodicity periodicity) {
		logger.info("Start to create all arff strings with periodicity "
						+ periodicity + "...");
		ArrayList<ArffParkingObject> arffStrings = new ArrayList<ArffParkingObject>();
		List<ParkingPlace> parkingPlaces = parkingUtil.retrieveParkingPlaces();
		ArffStringGenerator  arffStringGenerator = new ArffHistoryGenerator(config);
		for (ParkingPlace place : parkingPlaces) {
			String parkingId = place.getParkingId();
			logger.info("Start to create arff string for parkingplace " + parkingId);
			List<ParkingObservation> parkingObservations = parkingUtil.getPersistedParkingObservations(parkingId);
			parkingObservations = parkingUtil.constructStoredAndNewObservations(parkingObservations, place);
				parkingObservations = arffStringGenerator.filterObservationsTimespan(
						parkingObservations, periodicity);
			TSInterpolationFilter filter = this.config.getInterpolationStrategy().getInterpolationStrategy();
			if(filter!= null)
				filter.filterTimeseries(parkingObservations, periodicity);
			String arffString = arffStringGenerator.generateArff(
					parkingObservations, overlayAttributes);
			if (this.config.isWriteArff())
				ArffFileWriter.writeArffToFile(arffString, parkingId, periodicity, config);
			arffStrings.add(new ArffParkingObject(arffString,
					this.overlayAttributes, place));
		}
		logger.info("All arff strings with "+ periodicity+ " periodicity successfully created");
		return arffStrings;
	}

	/**
	 * this creates an arff string with only future instances. the number of
	 * future instances is defined in the in the application configuration
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @return the arff instances for the future
	 */
	public String generateFutureArff(ObservationPeriodicity periodicity) {
		ArffFutureGenerator arffFutureGenerator =
				new ArffFutureGenerator(periodicity, this.config);
		String futureArffString = arffFutureGenerator.generateArff(
					null, this.overlayAttributes);
		this.futureDates = arffFutureGenerator.getFutureDates();
		return futureArffString;
	}

	/**
	 * @return the name of the attribute that is used as timestamp in the
	 *         timeseries
	 */
	public static String getDateAttribute() {
		return ArffPreprocessor.DATEATTRIBUTE;
	}

	/**
	 * @return the name of the attribute that is used to forecast in the
	 *         timeseries
	 */
	public static String getForecastAttribute() {
		return ArffPreprocessor.FORECASTATTRIBUTE;
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


	/**
	 * @return the overlayAttributes
	 */
	public OverlayAttributes getOverlayAttributes() {
		return overlayAttributes;
	}


	/**
	 * @param overlayAttributes the overlayAttributes to set
	 */
	public void setOverlayAttributes(OverlayAttributes overlayAttributes) {
		this.overlayAttributes = overlayAttributes;
	}

	/**
	 * @return the futureDates
	 */
	public ArrayList<Timestamp> getFutureDates() {
		return futureDates;
	}


	/**
	 * @param futureDates the futureDates to set
	 */
	public void setFutureDates(ArrayList<Timestamp> futureDates) {
		this.futureDates = futureDates;
	}









}
