package it.unibz.tsmodel.overlay;


import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.dao.EventDao;
import it.unibz.tsmodel.dao.EventObservationDao;
import it.unibz.tsmodel.domain.Event;
import it.unibz.tsmodel.domain.EventObservation;
import it.unibz.tsmodel.domain.ObservationMetaInfo;

import java.sql.Timestamp;
import java.util.Calendar;
import java.util.HashMap;
import java.util.List;

import javax.annotation.PostConstruct;

import org.apache.commons.lang3.time.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;

/**
 * @author mreinstadler This class represents one event used as overlay
 *         attribute in the weka prediction process
 * 
 */
class EventOverlay implements OverlayAttribute {

	private final String attrName = "event";
	private final String attrFormat = "Numeric";
	private HashMap<Timestamp, EventObservation> events = null;
	@Autowired
	private EventDao eventDao;
	@Autowired
	private EventObservationDao eventObservationDao;
	@Autowired
	private TSModelConfig config;


	@PostConstruct
	public void init() {
		this.events = new HashMap<Timestamp, EventObservation>();
		Calendar cal = Calendar.getInstance();
		cal.add(Calendar.DAY_OF_YEAR, - config.getMaxHistoryDays());
		List<EventObservation> observations = eventObservationDao.
				findObservations(new Timestamp(cal.getTimeInMillis()));
		for(EventObservation obs : observations)
			events.put(obs.getTimestamp(), obs);
		
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
		String event = "0";
		Integer val = getEventId(time);
		if(val>0){
			if(strategy== OverlayStrategy.BOOL_VAL)
				event= "1";
			else
				event = val.toString();
		}
		return event;
	}

	/**
	 * @param timestamp the desired date
	 * @return the id of the observed holiday and -1 if there is no holiday
	 * observed
	 */
	private int getEventId(Timestamp timestamp){
		Timestamp time = new Timestamp(DateUtils.truncate
				(timestamp, Calendar.DAY_OF_MONTH).getTime());
		if (this.events.containsKey(time)){
			return events.get(time).getObservedValue();
		}
		else
			return -1;
	}
	
	@Override
	public ObservationMetaInfo getMetaInformation(Timestamp timestamp) {
		Timestamp time = new Timestamp(DateUtils.truncate
				(timestamp, Calendar.DAY_OF_MONTH).getTime());
		int eid = getEventId(time);
		if(eid>0)
			return eventDao.findEvent(eid);
		return new Event();
	}

	

}
