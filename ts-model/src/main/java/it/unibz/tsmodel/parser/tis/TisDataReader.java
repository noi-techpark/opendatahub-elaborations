package it.unibz.tsmodel.parser.tis;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;
import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import flexjson.JSONDeserializer;
import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.domain.ParkingPlace;

/**
 * this class is used to call the webservice of TIS to get the data about free
 * parking places in the past. For further information see
 * https://bitbucket.org/sipai/sipai-mobile/wiki/TIS%20Webservices
 * 
 * @author mreinstadler
 * @author Patrick Bertolla
 *
 */
class TisDataReader {

	private static final Log logger = LogFactory.getLog(TisDataReader.class);

	private static final String PROXY = "localhost";
	/**
	 * the url of the webservice determining the free slots
	 */
	private final static String OCCUPIED_URL = "http://ipchannels.integreen-life.bz.it/parking/rest/get-records-in-timeframe?name=occupied&station=";
	/**
	 * the url of the webservice determining the parking ids
	 */
	private final static String PARKINGIDS_URL = "http://ipchannels.integreen-life.bz.it/parking/rest/get-stations";

	private final static String PARKING_METADATA_URL = "http://ipchannels.integreen-life.bz.it/parking/rest/get-station-details";



	/**
	 * calls the web-service from TIS for the new {@link ParkingObservation}
	 * @param parkingId the id of the parking place
	 * @param fromDate the date from when the reader should read. Cannot be null
	 * @param config the configuration of the application
	 * @return the list of {@link ParkingObservation} found through tis webservice
	 * 
	 */
	//TODO: retrieve data from intime db
	public static ArrayList<ParkingObservation> retrieveFreeSlotss(String parkingId, Date fromDate, TSModelConfig config) {

		logger.info("Reading free slots of parking place "+ parkingId + " from webservice starting from " + fromDate);	
		ArrayList<ParkingObservation> res = new ArrayList<ParkingObservation>();
		if(fromDate==null){
			logger.equals("The date to read from the TIS webservice was null");
			return res;
		}
		Calendar now = Calendar.getInstance();
		int count =0;
		StringBuilder urlStringBuilder = new StringBuilder(OCCUPIED_URL);
		urlStringBuilder.append(parkingId);
		urlStringBuilder.append("&from=");
		urlStringBuilder.append(fromDate.getTime());
		urlStringBuilder.append("&to=");
		urlStringBuilder.append(now.getTimeInMillis());

		URL url;
		BufferedReader bufferedReader;
		try {
			url = new URL(urlStringBuilder.toString());
			//url = new URL("http", PROXY, 8080, urlStringBuilder.toString());
			URLConnection urlConnection = url.openConnection();
			urlConnection.setDoOutput(true);
			urlConnection.setAllowUserInteraction(false);
			bufferedReader = new BufferedReader(new InputStreamReader(
					urlConnection.getInputStream()));
			JSONDeserializer<ArrayList<Map<String,Object>>> jsonDeserializer = new JSONDeserializer<ArrayList<Map<String,Object>>>();
			ArrayList<Map<String,Object>> jsonResult = jsonDeserializer
					.deserialize(bufferedReader);
			for (Map<String,Object> singleResult : jsonResult) {
				Timestamp currentTimestamp = new Timestamp((Long) singleResult.get("timestamp"));
				int currentObservedValue = (Integer) singleResult.get("value");
				ParkingObservation newObservation= new ParkingObservation(currentTimestamp,currentObservedValue, parkingId);
				res.add(newObservation);
				count++;		
			}
			bufferedReader.close();

		} catch (IOException e) {
			logger.warn("fail to read free slots of parkingplace " + parkingId
					+ " from TIS webservice");
		}


		logger.info( "Finish reading free slots of "
				+ parkingId + " from webservice. Found " + count + " new observations");
		return res;
	}

	/**
	 * reads the free parking places from the webservice and returns an
	 * ArrayList of Integers representing the ids of the parking places
	 * @param config the configuration of the application
	 * @return the ids of the retrieve parking places. If no data is found, an
	 *         empty list of Integer objects is returned
	 * @throws IOException
	 */
	public static ArrayList<String> retrieveParkingIDs(TSModelConfig config) {
		ArrayList<String> parkingIds = new ArrayList<String>();
		logger.info("Reading parking id's from webservice...");

		URL url;
		try {
			url = new URL(PARKINGIDS_URL);
			//url = new URL("http", PROXY, 8080, PARKINGIDS_URL);
			URLConnection urlConnection = url.openConnection();
			urlConnection.setDoOutput(true);
			urlConnection.setAllowUserInteraction(false);
			BufferedReader bufferedReader = new BufferedReader(
					new InputStreamReader(urlConnection.getInputStream()));
			JSONDeserializer<ArrayList<String>> jsonDeserializer = new JSONDeserializer<ArrayList<String>>();
			parkingIds = jsonDeserializer.deserialize(bufferedReader);
			logger.info("Finish parsing parking ids. Found " + parkingIds.size() + " parking ids");
			bufferedReader.close();
		} catch (IOException e) {
			logger.warn(
					"fail to read the ids of the parking places");
			return parkingIds;
		}

		return parkingIds;
	}

	/**
	 * this method retrieves a {@link ParkingPlace} from the TIS webservice, 
	 * adds the newly found {@link ParkingObservation} to the {@link ParkingPlace}
	 * and persists them in the database
	 * @param parkingid
	 *            the id of the parking place
	 * @param config the configuration of the application
	 * @return the {@link ParkingPlace}, which holds all the metadata of the
	 *         required place
	 * @throws IOException
	 */
	public  static ParkingPlace retrieveParkingPlace(String parkingid, TSModelConfig config) {
		logger.info( "Construct parkingplace number " + parkingid
				+ " from webservice...");
		try {
			StringBuilder urlStringBuilder = new StringBuilder(
					PARKING_METADATA_URL);
			URL url;
			url = new URL(urlStringBuilder.toString());
			//url = new URL("http", PROXY, 8080, urlStringBuilder.toString());
			URLConnection urlConnection = url.openConnection();
			urlConnection.setDoOutput(true);
			urlConnection.setAllowUserInteraction(false);
			BufferedReader bufferedReader = new BufferedReader(
					new InputStreamReader(urlConnection.getInputStream()));
			JSONDeserializer<List<Map<String, Object>>> jsonDeserializer = new JSONDeserializer<List<Map<String, Object>>>();
			List<Map<String, Object>> stations = jsonDeserializer
					.deserialize(bufferedReader);
			Map<String, Object> metadata = findStation(stations,parkingid);
			ParkingPlace parkingplace = new ParkingPlace(metadata);
			parkingplace.setParkingId(parkingid);
			logger.info("Finish to construct parkingplace "
					+ parkingid + " from webservice");
			return parkingplace;
		} catch (IOException e) {
			logger.warn( "Fail to construct parkingplace "
					+ parkingid + " from webservice");
			return null;
		}
	}
	/**
	 * @param config the configuration of the application
	 * @return List of all station metadata provided by the noi webservice
	 */
	public static List<Map<String,Object>> retrieveParkingPlaces(TSModelConfig config) {
		logger.info("Sync parking places");
		try {
			StringBuilder urlStringBuilder = new StringBuilder(
					PARKING_METADATA_URL);
			URL url;
			url = new URL(urlStringBuilder.toString());
			//url = new URL("http", PROXY, 8080, urlStringBuilder.toString());
			URLConnection urlConnection = url.openConnection();
			urlConnection.setDoOutput(true);
			urlConnection.setAllowUserInteraction(false);
			BufferedReader bufferedReader = new BufferedReader(
					new InputStreamReader(urlConnection.getInputStream()));
			JSONDeserializer<List<Map<String, Object>>> jsonDeserializer = new JSONDeserializer<List<Map<String, Object>>>();
			List<Map<String, Object>> stations = jsonDeserializer
					.deserialize(bufferedReader);
			return stations;
		} catch (IOException e) {
			logger.warn( "Fail to retrieve parking stations metadata");
			return null;
		}
	}
	private static Map<String, Object> findStation(List<Map<String, Object>> stations, String parkingid) {
		for (Map<String, Object> station : stations) {
			if (station.get("id").toString().equals(parkingid))
				return station;
		}
		return null;
	}

	/**
	 * @return the freeslotsUrl
	 */
	public static String getFreeslotsUrl() {
		return OCCUPIED_URL;
	}

	/**
	 * @return the parkingidsUrl
	 */
	public static String getParkingidsUrl() {
		return PARKINGIDS_URL;
	}

	/**
	 * @return the parkingMetadataUrl
	 */
	public static String getParkingMetadataUrl() {
		return PARKING_METADATA_URL;
	}

}
