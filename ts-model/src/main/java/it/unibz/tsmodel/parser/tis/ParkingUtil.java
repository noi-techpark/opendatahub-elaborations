package it.unibz.tsmodel.parser.tis;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.time.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.dao.ParkingObservationDao;
import it.unibz.tsmodel.dao.ParkingPlaceDao;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.domain.ParkingPlace;

/**
 * this utility class performs all the actions on parking
 *         lots (stored in database and found through TIS webservice)
 * @author mreinstadler
 * @author Patrick Bertolla
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
	 * @param place
	 *            the parking place {@link ParkingObservation} found in the db
	 * @return the new list of {@link ParkingObservation} containing stored
	 * observations and newly found observation
	 */
	public List<ParkingObservation> constructStoredAndNewObservations(
			List<ParkingObservation> dbParkingObservations, ParkingPlace place) {
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
		ArrayList<ParkingObservation> newObservations = TisDataReader.retrieveFreeSlots(place, lastDate, config);
		ParkingObservation newestStored = dao.findNewestObservationsByPlace(place.getParkingId());
		for (ParkingObservation observation : newObservations) {
			if (newestStored == null || newestStored.getTimestamp().before(observation.getTimestamp())) {
				dao.persist(observation);
				result.add(observation);
			}
		}
		return result;
	}

	/**
	 * @return the list of {@link ParkingPlace} found in the database.
	 *         furthermore the tis webservice is asked for new places and they
	 *         are upserted
	 */
	public List<ParkingPlace> retrieveParkingPlaces() {

		List<ParkingPlace> storedPlaces = this.placeDao.findAllParkingPlaces();
		List<Map<String, Object>> wsStations = TisDataReader.retrieveParkingPlaces(config);
		upsertParkingPlaces(storedPlaces,wsStations);
		return storedPlaces;
	}



	/**
	 * Upserts current stations in db, using station metadata provided by tis-webservice
	 * @param storedPlaces places which are stored in the local db
	 * @param wsStations places which the tis webservice provides
	 */
	private void upsertParkingPlaces(List<ParkingPlace> storedPlaces, List<Map<String, Object>> wsStations) {
		for (Map<String, Object> parkingplace:wsStations) {
			String pid = parkingplace.get("id").toString();
			if (pid != null) {
				ParkingPlace storedPlace = placeContained(storedPlaces,pid);
				if (storedPlace != null) {
					storedPlace.setPhone((String) parkingplace.get("phonenumber"));
					storedPlace.setAdress((String) parkingplace.get("mainaddress"));
					storedPlace.setMaxSlots((Integer) parkingplace.get("capacity"));
					storedPlace.setName((String) parkingplace.get("name"));
					storedPlace.setDescription((String) parkingplace.get("name"));
					storedPlace.setLongitude((Double) parkingplace.get("longitude"));
					storedPlace.setLatitude((Double) parkingplace.get("latitude"));
					placeDao.merge(storedPlace);
				}
				else {
					ParkingPlace newPlace = new ParkingPlace(parkingplace);
					placeDao.persist(newPlace);
					storedPlaces.add(newPlace);
				}

			}

		}
	}

	private ParkingPlace placeContained(List<ParkingPlace> parkingPlaces, String pid) {
		if(parkingPlaces==null||parkingPlaces.isEmpty())
			return null;
		for (ParkingPlace p : parkingPlaces) {
			if (p.getParkingId().equals(pid))
				return p;
		}
		return null;
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
