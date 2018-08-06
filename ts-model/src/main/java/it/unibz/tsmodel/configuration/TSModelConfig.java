package it.unibz.tsmodel.configuration;

import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.model.strategy.AutomaticPeriodicAttrStrategy;
import it.unibz.tsmodel.model.strategy.BaseLearnerStrategy;
import it.unibz.tsmodel.model.strategy.EvaluationStrategy;
import it.unibz.tsmodel.model.strategy.LagStrategy;
import it.unibz.tsmodel.model.strategy.SkiplistStrategy;
import it.unibz.tsmodel.overlay.OverlayStrategy;
import it.unibz.tsmodel.parser.filter.DataInterpolationStrategy;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.apache.commons.lang3.time.DateUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;


/**
 * @author mreinstadler
 * reflects the ts-analysis.properties file with the
 * properties for general configurations and for the
 * model configurations. For information on the model configuration
 * see http://wiki.pentaho.com/display/DATAMINING/Time+Series+Analysis+and+Forecasting+with+Weka
 *
 */
public class TSModelConfig {
	
	private static final Log logger = LogFactory.getLog(TSModelConfig.class);
	//general configurations
	
	private String arffFileDirectory;
	
	private String dateFormat;
	
	private int forecastSteps;
	
	private double confidenceInterval;
	
	private String forecastDirectory;
	
	private boolean modelEvaluation;
	
	private boolean writeArff;
	
	private int maxHistoryDays;
	
	private String appStart;
	
	//the model strategies
	private String strategyOverlay;
	
	private String strategyBaselearner;
	
	private String strategyEvalution;
	
	private String strategyLag;
	
	private String strategyAutomaticperiodicity;
	
	private String strategySkiplist;
	//the observation periodicities used
	private boolean allObservationPeriodicity;
	
	private String dataInterpolation;
	
	
	
	/**
	 * Initializes the properties with default values
	 */
	public TSModelConfig() {
		this.arffFileDirectory= "resources/TSA-INF/arfffiles";
		this.dateFormat = "yyyy-MM-dd'T'HH:mm";
		this.forecastSteps= 24;
		this.confidenceInterval = 0.95;
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
		this.appStart = "2013-01-01T00:00";
		this.dataInterpolation= "NO_INTERPOL";
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
	 * @return the confidenceInterval
	 */
	public double getConfidenceInterval() {
		return confidenceInterval;
	}



	/**
	 * @param confidenceInterval the confidenceInterval to set
	 */
	public void setConfidenceInterval(double confidenceInterval) {
		this.confidenceInterval = confidenceInterval;
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
		for(OverlayStrategy o: OverlayStrategy.values()){
			if(o.name().equals(strategyOverlay))	
				this.strategyOverlay = strategyOverlay;
		}
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
		for(BaseLearnerStrategy b : BaseLearnerStrategy.values()){
			if(b.name().equals(strategyBaselearner))
				this.strategyBaselearner = strategyBaselearner;
		}
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
		for(EvaluationStrategy s: EvaluationStrategy.values()){
			if(s.name().equals(strategyEvalution))
				this.strategyEvalution = strategyEvalution;
		}
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
		for(LagStrategy s: LagStrategy.values()){
			if(s.name().equals(strategyLag))
				this.strategyLag = strategyLag;
		}
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
		for(AutomaticPeriodicAttrStrategy s: AutomaticPeriodicAttrStrategy.values()){
			if(s.name().equals(strategyAutomaticperiodicity))
				this.strategyAutomaticperiodicity = strategyAutomaticperiodicity;
		}
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
		for(SkiplistStrategy s: SkiplistStrategy.values()){
			if(s.name().equals(strategySkiplist))
				this.strategySkiplist = strategySkiplist;
		}
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
	 * @return the String representing the start date of the application
	 */
	public String getAppStart() {
		return appStart;
	}



	/**
	 * @param appStart the String representing the start date of the application
	 */
	public void setAppStart(String appStart) {
		this.appStart = appStart;
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



	/**
	 * @return the startdate of the application, which is 
	 * by default 1.1.2013
	 */
	public Date getAppStartDate(){
		Date date= new Date();
		try {
			date= DateUtils.parseDate(this.appStart,this.dateFormat);
		} catch (ParseException e) {
			logger.error("cannot parse the app start date; continue with the current date"); 
		}
		return date;
	}

	/**
	 * @return the {@link OverlayStrategy} of the model building process
	 */
	public OverlayStrategy getOverlayStrategy(){
		return OverlayStrategy.valueOf(this.strategyOverlay);
	}
	
	/**
	 * @return the {@link AutomaticPeriodicAttrStrategy} of the model building process
	 */
	public AutomaticPeriodicAttrStrategy getAutomaticPeriodicityStrategy(){
		return AutomaticPeriodicAttrStrategy.valueOf(this.strategyAutomaticperiodicity);
	}
	
	/**
	 * @return the {@link LagStrategy} of the model building process
	 */
	public LagStrategy getLagStrategy(){
		return LagStrategy.valueOf(this.strategyLag);
	}
	
	/**
	 * @return the {@link BaseLearnerStrategy} of the model building process
	 */
	public BaseLearnerStrategy getBaselearnerStrategy(){
		return BaseLearnerStrategy.valueOf(this.strategyBaselearner);
	}
	
	/**
	 * @return the {@link EvaluationStrategy} of the model building process
	 */
	public EvaluationStrategy getEvaluationStrategy(){
		return EvaluationStrategy.valueOf(this.strategyEvalution);
	}
	
	/**
	 * @return the {@link SkiplistStrategy} of the model building process
	 */
	public SkiplistStrategy getSkiplistStrategy(){
		return SkiplistStrategy.valueOf(this.strategySkiplist);
	}
	
	/**
	 * @return the {@link DataInterpolationStrategy}, which is used to clean faulty data in 
	 * the time-series
	 */
	public DataInterpolationStrategy getInterpolationStrategy(){
		return DataInterpolationStrategy.valueOf(this.dataInterpolation);
	}
	
	
	@Override 
	public String toString(){
		StringBuilder sb = new StringBuilder();
		String nl = System.getProperty("line.separator");
		sb.append("arff directory: "+ this.arffFileDirectory+ nl);
		sb.append("dateformat: "+ this.dateFormat+ nl);
		sb.append("forecast directory: "+ this.forecastDirectory+ nl);
		sb.append("forecaststeps: "+ this.forecastSteps+ nl);
		sb.append("confidence interval: "+ this.confidenceInterval+ nl);
		sb.append("overlay strategy: "+ this.strategyOverlay+ nl);
		sb.append("periodicity strategy: "+ this.strategyAutomaticperiodicity+ nl);
		sb.append("baselearner strategy: "+ this.strategyBaselearner+ nl);
		sb.append("evalution strategy: "+ this.strategyEvalution+ nl);
		sb.append("lag strategy: "+ this.strategyLag+ nl);
		sb.append("skiplist strategy: "+ this.strategySkiplist+ nl);
		sb.append("all observation periodicities: "+ this.isAllObservationPeriodicity()+ nl);
		sb.append("maximum history: "+ this.maxHistoryDays+ nl);
		sb.append("appstart at: "+ this.appStart+ nl);
		return sb.toString();
	}

	
	

}
