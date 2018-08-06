package it.unibz.tsmodel.model.strategy;

/**
 * @author mreinstadler
 * the skip-list used for the timeseries
 * (e.g. the hours between 22.00 and 06.00
 * in the morning should be skipped)
 *
 */
public enum SkiplistStrategy {
	NO_SKIPLIST, 
	
	/**
	 *take care, it is very time consuming 
	 */
	SKIPLIST

}
