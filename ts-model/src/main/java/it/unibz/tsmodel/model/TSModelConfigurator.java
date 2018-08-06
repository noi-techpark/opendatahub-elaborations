package it.unibz.tsmodel.model;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.model.strategy.AutomaticPeriodicAttrStrategy;
import it.unibz.tsmodel.model.strategy.LagStrategy;
import it.unibz.tsmodel.overlay.OverlayAttribute;
import it.unibz.tsmodel.overlay.OverlayAttributes;
import it.unibz.tsmodel.overlay.OverlayStrategy;
import it.unibz.tsmodel.parser.TimeSeries;

import java.util.ArrayList;
import java.util.List;

import weka.classifiers.timeseries.WekaForecaster;
import weka.classifiers.timeseries.core.TSLagMaker.Periodicity;

/**
 * this class is used to configure the learner algorithm. details about the
 * configuration are explained in the WEKA documentation
 * http://wiki.pentaho.com/
 * display/DATAMINING/Time+Series+Analysis+and+Forecasting+with+Weka
 * 
 * @author mreinstadler
 * 
 */
class TSModelConfigurator {

	

	/**
	 * this configures the learner algorithm. the specific settings are
	 * explained in the weka documentation
	 * http://wiki.pentaho.com/display/DATAMINING
	 * /Time+Series+Analysis+and+Forecasting+with+Weka
	 * 
	 * @param forecaster
	 *            the {@link WekaForecaster} without specific configuration
	 * @param overlayAttrs
	 *            the list of {@link OverlayAttribute}
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @param config the configuration of the application
	 * @throws Exception
	 */
	public static void configureForecaster(WekaForecaster forecaster,
			OverlayAttributes overlayAttrs, ObservationPeriodicity periodicity, 
			TSModelConfig config) throws Exception {
		forecaster.reset();
		forecaster.setFieldsToForecast(TimeSeries.getForecastAttribute());
		forecaster.getTSLagMaker().setPeriodicity(Periodicity.UNKNOWN);
		forecaster.setBaseForecaster(config.getBaselearnerStrategy().getClassifierStrategy());
		forecaster.getTSLagMaker().setTimeStampField(
				TimeSeries.getDateAttribute());
		LagStrategy lagStrategy = config.getLagStrategy();
		AutomaticPeriodicAttrStrategy periodStrategy = config.getAutomaticPeriodicityStrategy();
		OverlayStrategy overlayStrategy = config.getOverlayStrategy();
		forecaster.getTSLagMaker().setMinLag(lagStrategy.getMinLag());
		forecaster.getTSLagMaker().setMaxLag(getMaxLags(periodicity, lagStrategy));
		if(lagStrategy==LagStrategy.EXTENDED_LAG)
			forecaster.getTSLagMaker().setFineTuneLags(getFineTuneLags(periodicity));
		forecaster.getTSLagMaker().setAddAMIndicator(periodStrategy.isAm());
		forecaster.getTSLagMaker().setAddDayOfMonth(periodStrategy.isDayOfMonth());
		forecaster.getTSLagMaker().setAddDayOfWeek(periodStrategy.isDayOfWeek());
		forecaster.getTSLagMaker().setAddQuarterOfYear(periodStrategy.isQuarter());
		forecaster.getTSLagMaker().setAddWeekendIndicator(periodStrategy.isWeekend());
		forecaster.getTSLagMaker().setAddMonthOfYear(periodStrategy.isMonth());
		if (overlayStrategy != OverlayStrategy.NO_OVERLAY) {
			if (overlayAttrs != null && overlayAttrs.getOverlayAttributes().size() > 0) {
				List<String> overlay = new ArrayList<String>();
				for (OverlayAttribute ov : overlayAttrs.getOverlayAttributes()) {
					overlay.add(ov.getAttributeName());
				}
				forecaster.getTSLagMaker().setOverlayFields(overlay);

			}
		}
		if(config.isModelEvaluation()){
			forecaster.setConfidenceLevel(config.getConfidenceInterval());
			forecaster.setCalculateConfIntervalsForForecasts(config.getForecastSteps());
		}
	}
	
	/**
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @param lagstrategy the strategy used to create lag variables
	 * @return the max amount of lag variables
	 */
	private static int getMaxLags(ObservationPeriodicity periodicity, LagStrategy lagstrategy){
		int multiplier = 60/periodicity.minutes();
		int res = lagstrategy.getMaxLag()* multiplier;
		if(lagstrategy == LagStrategy.EXTENDED_LAG)
			res++;
		return res;
		
	}
	
	/**
	 * @param periodicity tthe time distance between {@link ParkingObservation}
	 * @return the finetuned lag string (based on the periodicity), which respects the whole week
	 */
	public static String getFineTuneLags(ObservationPeriodicity periodicity){
		int hourMultiplier= 60/periodicity.minutes();
		int []weekHours= new int[7];
		for(int a=0; a<7 ; a++){
			weekHours[a]= 24*hourMultiplier*(a+1);
		}
		StringBuilder result = new StringBuilder("1-"+ weekHours[0]);
		for(int b=1; b<weekHours.length; b++){
			result.append("," + (weekHours[b]-1)+"-"+ (weekHours[b]+1));
		}
		return result.toString();
	}
	

}
