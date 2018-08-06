package it.unibz.tsmodel.parser.tis;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.dao.ParkingObservationDao;
import it.unibz.tsmodel.dao.ParkingPlaceDao;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.domain.ParkingPlace;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import org.apache.commons.lang3.time.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * @author mreinstadler this utility class performs all the actions on parking
 *         lots (stored in database and found through TIS webservice)
 * 
 */
public class ParkingUtil {

	@Autowired
	private ParkingObservationDao dao;
	@Autowired
	private ParkingPlaceDao placeDao;
	@Autowired
	private TSModelConfig config;

	/**
	 * adds new {@link ParkingObservation} found through Tis webservice to the
	 * already stored {@link ParkingObservation} in database
	 * 
	 * @param dbParkingObservations
	 *            the {@link ParkingObservation} s found in the db
	 * @param parkingId
	 *            the id of the {@link ParkingObservation} s found in the db
	 * @return the new list of {@link ParkingObservation} containing stored 
	 * observations and newly found observation
	 */
	public List<ParkingObservation> constructStoredAndNewObservations( 
			List<ParkingObservation> dbParkingObservations, String parkingId) {
		Date lastDate= Calendar.getInstance().getTime();
		List<ParkingObservation> result;
		if (dbParkingObservations == null || dbParkingObservations.isEmpty()) {
			result = new ArrayList<ParkingObservation>();
			lastDate = this.config.getAppStartDate();
		} else{
			result = dbParkingObservations;
			lastDate = result.get(
					result.size() - 1).getTimestamp();
			lastDate = DateUtils.addMinutes(lastDate, 5);
		}
		ArrayList<ParkingObservation> newObservations = TisDataReader.retrieveFreeSlotss(parkingId, lastDate, config);
		for (ParkingObservation observation : newObservations) {
			if (result.isEmpty() || observation.getTimestamp().after(
					result.get(result.size() - 1)
							.getTimestamp())) {
					dao.persist(observation);
					result.add(observation);
			}
		}
		return result;
	}

	/**
	 * @return the list of {@link ParkingPlace} found in the database.
	 *         furthermore the tis webservice is asked for new places and they
	 *         are saved and added to that list
	 */
	public List<ParkingPlace> retrieveParkingPlaces() {
		List<ParkingPlace> storedPlaces = this.placeDao.findAllParkingPlaces();
		ArrayList<String> tisPids = TisDataReader.retrieveParkingIDs(config);
		for (String pid : tisPids) {
			if (!placeContained(storedPlaces, pid)) {
				ParkingPlace newPlace = TisDataReader.retrieveParkingPlace(pid, config);
				placeDao.persist(newPlace);
				storedPlaces.add(newPlace);	
			}
		}
		return storedPlaces;
	}

	

	/**
	 * @param parkingPlaces
	 *            the list of {@link ParkingPlace}. can be null
	 * @param pid
	 *            the id of the {@link ParkingPlace}
	 * @return true if the list contains the {@link ParkingPlace} with the
	 *         requested id
	 */
	private boolean placeContained(List<ParkingPlace> parkingPlaces, String pid) {
		if(parkingPlaces==null||parkingPlaces.isEmpty())
			return false;
		for (ParkingPlace p : parkingPlaces) {
			if (p.getParkingId().equals(pid))
				return true;
		}
		return false;
	}

	/**
	 * @param pid
	 *            the id of the {@link ParkingPlace}
	 * @return the list of {@link ParkingObservation} corresponding to the place
	 */
	public List<ParkingObservation> getPersistedParkingObservations(String pid) {
		Calendar cal = Calendar.getInstance();
		cal.add(Calendar.DAY_OF_YEAR, -config.getMaxHistoryDays());
		return this.dao.findObservationsByPlace(pid,
				new Timestamp(cal.getTimeInMillis()));
	}

}
