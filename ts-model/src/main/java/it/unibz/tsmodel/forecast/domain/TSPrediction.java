package it.unibz.tsmodel.forecast.domain;

import weka.classifiers.evaluation.NumericPrediction;
import weka.classifiers.evaluation.Prediction;




/**
 * @author mreinstadler This class represents one single prediction of a 
 * parking lot. It contains the predicted value, the confidence bounds
 * (lower and upper) and the occupancy status (free or occupied)
 */
public class TSPrediction{

	private Integer predictedFreeSlots;
	private double upperConfidenceLevel;
	private double lowerConfidenceLevel;
	private String status;
	private final static String OCCUPIED = "occupied";
	private final static String UNSECURE = "unsecure";
	private final static String FREE = "free";
	
	


	

	
	/**
	 * @param slots
	 *            the predicted free slots
	 * @param upperConf
	 *            the upper limit of the confidence interval
	 * @param lowerConf
	 * 			the lower limit of the confidence interval
	 */	
	public TSPrediction(int slots, double upperConf, double lowerConf) {
		
		this.predictedFreeSlots = slots;
		this.lowerConfidenceLevel = lowerConf;
		this.upperConfidenceLevel= upperConf;
		if(this.predictedFreeSlots<=0)
			this.status= OCCUPIED;
		else if(this.lowerConfidenceLevel<=0)
			this.status= UNSECURE;
		else
			this.status= FREE;
				
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
