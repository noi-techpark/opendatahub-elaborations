package it.unibz.tsmodel.model.strategy;

/**
 * @author mreinstadler
 * the strategy of using automatically derived periodic attributes
 * in the timeseries or not. These attributes are am-pm, dayOfWeek, 
 * dayOfMonth, weekend, month, quarter
 *
 */
public enum AutomaticPeriodicAttrStrategy {
	NO_PERIODICITY(false,false,false,false,false,false),
	PERIODICITY(true,true,true,true,true,true);
	private final boolean am;
	private final boolean dayOfWeek;
	private final boolean dayOfMonth;
	private final boolean weekend;
	private final boolean month;
	private final boolean quarter;
	private AutomaticPeriodicAttrStrategy(boolean am, boolean dayOfWeek, boolean dayOfMonth,
			boolean weekend, boolean month, boolean quarter) {
		this.am = am;
		this.dayOfWeek = dayOfWeek;
		this.dayOfMonth = dayOfMonth;
		this.weekend = weekend;
		this.month = month;
		this.quarter = quarter;
	}
	/**
	 * @return the usage of am-pm in this strategy
	 */
	public boolean isAm() {
		return am;
	}
	/**
	 * @return the usage of automatically derived dayOfWeek 
	 * in this strategy
	 */
	public boolean isDayOfWeek() {
		return dayOfWeek;
	}
	/**
	 * @return the usage of automatically derived dayOfMonth 
	 * in this strategy
	 */
	public boolean isDayOfMonth() {
		return dayOfMonth;
	}
	/**
	 * @return the usage of automatically derived weekend 
	 * in this strategy
	 */
	public boolean isWeekend() {
		return weekend;
	}
	/**
	 * @return the usage of automatically derived month 
	 * in this strategy
	 */
	public boolean isMonth() {
		return month;
	}
	/**
	 * @return the usage of automatically derived quarter 
	 * in this strategy
	 */
	public boolean isQuarter() {
		return quarter;
	}


}
