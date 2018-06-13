package it.unibz.tsforecast.domain;




/**
 * @author mreinstadler This class represents one single prediction for the free
 *         slots. Actually it holds only the predicted value and the mean error
 *         of prediction calculated by the {@link ModelEvaluator}
 */
public class TSPrediction{

	private Integer predictedFreeSlots;
	private double upperConfidenceLevel;
	private double lowerConfidenceLevel;
	private String status;
//	private final static String OCCUPIED = "occupied";
//	private final static String UNSECURE = "unsecure";
//	private final static String FREE = "free";
	
	


	

	
	/**
	 * @param slots
	 *            the predicted free slots
	 * @param upperConf
	 *            the upper limit of the confidence interval
	 * @param lowerConf
	 * 			the lower limit of the confidence interval
	 * @param status
	 * ths status of the parking place (free or occupied)
	 */	
	public TSPrediction(int slots, double lowerConf, double upperConf, String status ) {
		
		this.predictedFreeSlots = slots;
		this.lowerConfidenceLevel = lowerConf;
		this.upperConfidenceLevel= upperConf;
		this.status = status;
			
	}

	/**
	 * @return the predicted free slots
	 */
	public Integer getPredictedFreeSlots() {
		return predictedFreeSlots;
	}

	
	/**
	 * @return the status of the parking place (free or occupied)
	 */
	public String getStatus() {
		return this.status;
	}

	/**
	 * @return the upperConfidenceLevel
	 */
	public double getUpperConfidenceLevel() {
		return upperConfidenceLevel;
	}

	/**
	 * @return the lowerConfidenceLevel
	 */
	public double getLowerConfidenceLevel() {
		return lowerConfidenceLevel;
	}

	
	

}
