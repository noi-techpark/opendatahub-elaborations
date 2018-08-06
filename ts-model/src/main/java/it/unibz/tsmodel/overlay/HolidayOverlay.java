package it.unibz.tsmodel.overlay;
import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.dao.HolidayDao;
import it.unibz.tsmodel.dao.HolidayObservationDao;
import it.unibz.tsmodel.domain.Holiday;
import it.unibz.tsmodel.domain.HolidayObservation;
import it.unibz.tsmodel.domain.ObservationMetaInfo;

import java.sql.Timestamp;
import java.util.Calendar;
import java.util.HashMap;
import java.util.List;

import javax.annotation.PostConstruct;

import org.apache.commons.lang3.time.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * @author mreinstadler This class represents one holiday used as overlay
 *         attribute in the weka prediction process
 * 
 */
class HolidayOverlay implements OverlayAttribute {

	private final String attrName = "holiday";
	private final String attrFormat = "Numeric";
	private HashMap<Timestamp, HolidayObservation> holidays = null;
	@Autowired
	private HolidayDao holidayDao;
	@Autowired
	private HolidayObservationDao holidayObservationDao;
	@Autowired
	private TSModelConfig config;
	

	public HolidayOverlay(){
		
	}
	/**
	 * Constructs the holiday overlay by initializing the list of 
	 * overlay values 
	 */
	@PostConstruct
	public void init() {
		this.holidays = new HashMap<Timestamp, HolidayObservation>();
		Calendar cal = Calendar.getInstance();
		cal.add(Calendar.DAY_OF_YEAR, - config.getMaxHistoryDays());
		List<HolidayObservation> observations = holidayObservationDao.
				findObservations(new Timestamp(cal.getTimeInMillis()));
		for(HolidayObservation obs : observations)
			holidays.put(obs.getTimestamp(), obs);
	}
	
	@Override
	public String getAttributeName() {
		return this.attrName;
	}

	@Override
	public String getAttributeFormat() {
		return this.attrFormat;
	}

	@Override
	public String getAttributeValue(Timestamp timestamp, OverlayStrategy strategy) {
		Timestamp time = new Timestamp(DateUtils.truncate
				(timestamp, Calendar.DAY_OF_MONTH).getTime());
		String holiDay = "0";
		Integer val = getHolidayId(time);
		if(val>0){
			if(strategy== OverlayStrategy.BOOL_VAL)
				holiDay= "1";
			else
				holiDay = val.toString();
		}
		return holiDay;
	}
	
	/**
	 * @param timestamp the desired date
	 * @return the id of the observed holiday and -1 if there is no holiday
	 * observed
	 */
	private int getHolidayId(Timestamp timestamp){
		Timestamp time = new Timestamp(DateUtils.truncate
				(timestamp, Calendar.DAY_OF_MONTH).getTime());
		if (this.holidays.containsKey(time)){
			return holidays.get(time).getObservedValue();
		}
		else
			return -1;
	}

	@Override
	public ObservationMetaInfo getMetaInformation(Timestamp timestamp) {
		Timestamp time = new Timestamp(DateUtils.truncate
				(timestamp, Calendar.DAY_OF_MONTH).getTime());
		int hid = getHolidayId(time);
		if(hid>0)
			return holidayDao.findHoliday(hid);
		return new Holiday();
	}

	

}
