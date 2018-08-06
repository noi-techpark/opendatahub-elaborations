package it.unibz.tsmodel.forecast;
import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;
import it.unibz.tsmodel.forecast.domain.ForecastStep;
import it.unibz.tsmodel.forecast.domain.ForecastSteps;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.io.xml.DomDriver;

/**
 * @author mreinstadler This class is responsible for the serialization of forecasts to and from XML
 * 
 */
class ForecastXMLSerializer {
	private final Log logger = LogFactory.getLog(ForecastXMLSerializer.class);
	private ForecastSteps allForecasts = null;
	private XStream xstream = null;

	
	
	/**
	 * initializes the serializer by configuring the 
	 * {@link XStream} object
	 */
	public ForecastXMLSerializer(){
		this.xstream = new XStream(new DomDriver());
		this.xstream.autodetectAnnotations(true);
		this.xstream.processAnnotations(ForecastSteps.class);		
	}
	
	/**
	 * @param forecastSteps
	 *            the list of {@link ForecastStep}
	 * @param periodicity the time distance between {@link ParkingObservation}
	 * @param config the configuration of the application
	 * @throws IOException
	 */
	public void serializeXML(ArrayList<ForecastStep> forecastSteps, ObservationPeriodicity periodicity, TSModelConfig config)
			throws IOException {
		File forecastFile = new File(config.getForecastDirectory()+ 
				File.separator + "forecast_"+periodicity+".xml");
		logger.info("Start writing forecasts to " + forecastFile.getAbsolutePath());
		if(forecastFile.exists())
			forecastFile.delete();
		forecastFile.createNewFile();
		allForecasts = new ForecastSteps(forecastSteps);
		OutputStream outputStream = new FileOutputStream(forecastFile);
		this.xstream.toXML(allForecasts, outputStream);
		outputStream.close();
		logger.info("Finish writing forecasts to " + forecastFile.getName());

	}

	
	/**
	 * @return the configured {@link XStream} XML streamer
	 */
	public XStream getConfiguredStreamer(){
		return this.xstream;
	}

}
