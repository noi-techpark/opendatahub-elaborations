package it.unibz.tsmodel.parser.filter;

public enum DataInterpolationStrategy {
	AUTO_INTERPOLATION(new TSAutoInterpolFilter()), 
	MANUAL_INTERPOLATION(new TSManualInterpolFilter()), 
	NO_INTERPOLATION(null);
	private final TSInterpolationFilter filter;
	private DataInterpolationStrategy(TSInterpolationFilter filter){
		this.filter = filter;
	}
	
	/**
	 * @return the strategy for data- interpolation in the 
	 * time-series
	 */
	public TSInterpolationFilter getInterpolationStrategy(){
		return this.filter;
	}

}
