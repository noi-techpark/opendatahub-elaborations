package it.unibz.tsmodel.domain;


/**
 * @author mreinstadler 
 * this describes the time distance between two {@link ParkingObservation} 
 * currently only hourly periodicity is allowed, because otherwise the java 
 * heap must be very large
 */
public enum ObservationPeriodicity {
	HALFHOURLY(30,"22:00@HH:mm,22:30@HH:mm,23:00@HH:mm,23:30@HH:mm,00:00@HH:mm,00:30@HH:mm,01:00@HH,"
			+ "01:30@HH:mm,02:00@HH:mm,2:30@HH:mm"
			+ ",03:00@HH:mm,03:30@HH:mm,04:00@HH:mm,04:30@HH:mm,"
			+ "05:00@HH:mm,05:30@HH:mm,06:00@HH:mm"),
	HOURLY(60, "22@HH,23@HH,00@HH,1@HH,2@HH,3@HH,4@HH,5@HH,6@HH");
	private final int minutes;
	private final String skiplist;
	
	private ObservationPeriodicity(int minutes, String skiplist) {
		this.minutes = minutes;
		this.skiplist = skiplist;
	} 
	/**
	 * @return the amount of minutes of this periodicity (e.g. hourly has
	 * a periodicity of 60 minutes)
	 */
	public int minutes(){
		return this.minutes;
	}
	
	/**
	 * @return the skiplist for the weka classification
	 */
	public String getSkiplist() {
		return skiplist;
	}
	
	
}
