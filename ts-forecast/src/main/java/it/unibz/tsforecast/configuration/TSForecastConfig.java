// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsforecast.configuration;
import it.unibz.tsforecast.entity.ObservationPeriodicity;

import java.text.DateFormat;
import java.text.SimpleDateFormat;


/**
 * @author mreinstadler
 * reflects the ts-analysis.properties file with the
 * properties for general configurations and for the
 * model configurations. For information on the model configuration
 * see http://wiki.pentaho.com/display/DATAMINING/Time+Series+Analysis+and+Forecasting+with+Weka
 *
 */
public class TSForecastConfig {
	//general configurations
	
	private String arffFileDirectory;
	
	private String dateFormat;
	
	private int forecastSteps;
	
	private String forecastDirectory;
	
	private boolean modelEvaluation;
	
	private boolean writeArff;
	
	private String appStart;
	
	//the model strategies
	private String strategyOverlay;
	
	private String strategyBaselearner;
	
	private String strategyEvalution;
	
	private String strategyLag;
	
	private String strategyAutomaticperiodicity;
	
	private String strategySkiplist;
	
	private double confidenceLevel;
	//the observation periodicities used
	private boolean allObservationPeriodicity;
	
	private int maxHistoryDays;
	
	private String dataInterpolation;
	
	/**
	 * Initializes the properties with default values
	 */
	public TSForecastConfig() {
		this.arffFileDirectory= "resources/TSA-INF/arfffiles";
		this.dateFormat = "yyyy-MM-dd'T'HH:mm";
		this.forecastSteps= 24;
		this.forecastDirectory= "resources/TSA-INF/forecasts";
		this.modelEvaluation= true;
		this.writeArff= true;
		this.strategyOverlay= "BOOL_VAL";
		this.strategyAutomaticperiodicity ="PERIODICITY";
		this.strategyBaselearner="LINREG";
		this.strategyEvalution= "TRAINING";
		this.strategyLag= "SIMPLE_LAG";
		this.strategySkiplist="NO_SKIPLIST";
		this.allObservationPeriodicity = false;
		this.maxHistoryDays = 730;
		this.confidenceLevel= 0.95;
	}



	/**
	 * @return the arffFileDirectory where the arff files are saved
	 */
	public String getArffFileDirectory() {
		return arffFileDirectory;
	}



	/**
	 * @param arffFileDirectory the arffFileDirectory to set
	 */
	public void setArffFileDirectory(String arffFileDirectory) {
		this.arffFileDirectory = arffFileDirectory;
	}



	/**
	 * @return the dateFormat (standard dateformat of the application)
	 */
	public String getDateFormat() {
		return dateFormat;
	}



	/**
	 * @param dateFormat the dateFormat (standard dateformat of the application) to set
	 */
	public void setDateFormat(String dateFormat) {
		this.dateFormat = dateFormat;
	}



	/**
	 * @return the forecastSteps - the number of steps to predict free slots
	 * the steps can be in minutes, quarter hours or half hours. See 
	 * {@link ObservationPeriodicity}
	 */
	public int getForecastSteps() {
		return forecastSteps;
	}



	/**
	 * @param forecastSteps the forecastSteps the number of steps to predict free slots
	 * the steps can be in minutes, quarter hours or half hours. See 
	 * {@link ObservationPeriodicity}
	 */
	public void setForecastSteps(int forecastSteps) {
		this.forecastSteps = forecastSteps;
	}



	/**
	 * @return the forecastDirectory where the forecast.xml file are stored
	 */
	public String getForecastDirectory() {
		return forecastDirectory;
	}



	/**
	 * @param forecastDirectory the forecastDirectory to set
	 */
	public void setForecastDirectory(String forecastDirectory) {
		this.forecastDirectory = forecastDirectory;
	}



	/**
	 * @return true if the model should be evaluated (time-consuming)
	 */
	public boolean isModelEvaluation() {
		return modelEvaluation;
	}



	/**
	 * @param modelEvaluation true if the model should be evaluated (time-consuming)
	 */
	public void setModelEvaluation(boolean modelEvaluation) {
		this.modelEvaluation = modelEvaluation;
	}



	/**
	 * @return true if arff should be written to file
	 */
	public boolean isWriteArff() {
		return writeArff;
	}



	/**
	 * @param writeArff true if arff should be written to file
	 */
	public void setWriteArff(boolean writeArff) {
		this.writeArff = writeArff;
	}



	
	
	
	/**
	 * @return the {@link DateFormat} used application wide
	 */
	public DateFormat getDateformatInUse(){
		return new SimpleDateFormat(this.dateFormat);
	}
	
	
	/**
	 * @return the strategy_overlay
	 * NO_OVERLAY,BOOL_VAL (default), REAL_VAL
	 */
	public String getStrategyOverlay() {
		return strategyOverlay;
	}
	/**
	 * @param strategyOverlay the strategy_overlay to set
	 * NO_OVERLAY,BOOL_VAL (default), REAL_VAL
	 */
	public void setStrategyOverlay(String strategyOverlay) {
		
				this.strategyOverlay = strategyOverlay;
		
	}
	/**
	 * @return the strategy_baselearner
	 * M5RULE, LINREG (default)
	 */
	public String getStrategyBaselearner() {
		return strategyBaselearner;
	}
	/**
	 * @param strategyBaselearner the strategy_baselearner to set
	 * M5RULE, LINREG (default)
	 */
	public void setStrategyBaselearner(String strategyBaselearner) {
		
				this.strategyBaselearner = strategyBaselearner;
		
	}
	/**
	 * @return the strategy_evalution
	 * TRAINING (default), TEST
	 */
	public String getStrategyEvalution() {
		return strategyEvalution;
	}
	/**
	 * @param strategyEvalution the strategy_evalution to set
	 * TRAINING (default), TEST
	 */
	public void setStrategyEvalution(String strategyEvalution) {
		
				this.strategyEvalution = strategyEvalution;
		
	}
	/**
	 * @return the strategy_lag
	 * SIMPLE_LAG (default), EXTENDED
	 */
	public String getStrategyLag() {
		return strategyLag;
	}
	/**
	 * @param strategyLag the strategy_lag to set
	 * SIMPLE_LAG (default), EXTENDED
	 */
	public void setStrategyLag(String strategyLag) {
		
				this.strategyLag = strategyLag;
		
	}
	/**
	 * @return the strategy_automaticperiodicity
	 * NO_PERIODICITY, PERIODICITY (default)
	 */
	public String getStrategyAutomaticperiodicity() {
		return strategyAutomaticperiodicity;
	}
	/**
	 * @param strategyAutomaticperiodicity the strategy_automaticperiodicity to set
	 * NO_PERIODICITY, PERIODICITY (default)
	 */
	public void setStrategyAutomaticperiodicity(
			String strategyAutomaticperiodicity) {
		
				this.strategyAutomaticperiodicity = strategyAutomaticperiodicity;
		
	}
	/**
	 * @return the strategy_skiplist
	 * NO_SKIPLIST, SKIPLIST (default)
	 */
	public String getStrategySkiplist() {
		return strategySkiplist;
	}
	/**
	 * @param strategySkiplist the strategy_skiplist to set
	 * NO_SKIPLIST, SKIPLIST (default)
	 */
	public void setStrategySkiplist(String strategySkiplist) {
		
				this.strategySkiplist = strategySkiplist;
		
	}
	
	
	/**
	 * @return the useAllObservationPeriodicities
	 */
	public boolean isAllObservationPeriodicity() {
		return allObservationPeriodicity;
	}



	/**
	 * @param useAllObservationPeriodicities the useAllObservationPeriodicities to set
	 */
	public void setAllObservationPeriodicity(
			boolean useAllObservationPeriodicities) {
		this.allObservationPeriodicity = useAllObservationPeriodicities;
	}

	

	/**
	 * @return the maxHistoryDays
	 */
	public int getMaxHistoryDays() {
		return maxHistoryDays;
	}



	/**
	 * @param maxHistoryDays the maxHistoryDays to set
	 */
	public void setMaxHistoryDays(int maxHistoryDays) {
		this.maxHistoryDays = maxHistoryDays;
	}


	
	
	/**
	 * @return the appStart
	 */
	public String getAppStart() {
		return appStart;
	}



	/**
	 * @param appStart the appStart to set
	 */
	public void setAppStart(String appStart) {
		this.appStart = appStart;
	}

	

	/**
	 * @return the confidenceLevel
	 */
	public double getConfidenceLevel() {
		return confidenceLevel;
	}



	/**
	 * @param confidenceLevel the confidenceLevel to set
	 */
	public void setConfidenceLevel(double confidenceLevel) {
		this.confidenceLevel = confidenceLevel;
	}



	/**
	 * @return the dataInterpolation
	 */
	public String getDataInterpolation() {
		return dataInterpolation;
	}



	/**
	 * @param dataInterpolation the dataInterpolation to set
	 */
	public void setDataInterpolation(String dataInterpolation) {
		this.dataInterpolation = dataInterpolation;
	}



	@Override 
	public String toString(){
		StringBuilder sb = new StringBuilder();
		String nl = System.getProperty("line.separator");
		sb.append("arff directory: "+ this.arffFileDirectory+ nl);
		sb.append("dateformat: "+ this.dateFormat+ nl);
		sb.append("forecast directory: "+ this.forecastDirectory+ nl);
		sb.append("forecaststeps: "+ this.forecastSteps+ nl);
		sb.append("overlay strategy: "+ this.strategyOverlay+ nl);
		sb.append("periodicity strategy: "+ this.strategyAutomaticperiodicity+ nl);
		sb.append("baselearner strategy: "+ this.strategyBaselearner+ nl);
		sb.append("evalution strategy: "+ this.strategyEvalution+ nl);
		sb.append("lag strategy: "+ this.strategyLag+ nl);
		sb.append("skiplist strategy: "+ this.strategySkiplist+ nl);
		sb.append("all observation periodicities: "+ this.isAllObservationPeriodicity()+ nl);
		sb.append("maximum history: "+ this.maxHistoryDays+ nl);
		sb.append("confidence level: "+ this.confidenceLevel + nl);
		return sb.toString();
	}

	
	

}
