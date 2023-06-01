// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.overlay.weather;

import it.unibz.tsmodel.domain.MeteoObservation;

import java.sql.Timestamp;
import java.util.ArrayList;

import com.google.gson.Gson;

/**
 * 
 * @author mreinstadler This class corresponds to one meteo observation coming
 *         from the OpenWeatherMap JSon string.
 */
class OWMObservations {
	private String message;
	private String code;
	private int city_id;
	private double calctime;
	private int cnt;
	private ArrayList<OWMObservation> list;
	
	public OWMObservations(){
		this.message="";
		this.code= "";
		this.city_id= -1;
		this.calctime= 0;
		this.cnt= -1;
		this.list= new ArrayList<OWMObservation>();
	}

	protected String getMessage() {
		return message;
	}

	protected void setMessage(String message) {
			if(message!= null)
		this.message = message;
	}

	protected String getCode() {
		return code;
	}

	protected void setCode(String code) {
		if(code!= null)
		this.code = code;
	}

	protected int getCity_id() {
		return city_id;
	}

	protected void setCity_id(int city_id) {
		
		this.city_id = city_id;
	}

	protected double getCalctime() {
		return calctime;
	}

	protected void setCalctime(double calctime) {
		this.calctime = calctime;
	}

	protected int getCnt() {
		return cnt;
	}

	protected void setCnt(int cnt) {
		this.cnt = cnt;
	}

	protected ArrayList<OWMObservation> getList() {
		return list;
	}

	protected void setList(ArrayList<OWMObservation> list) {
		if(list!= null)
		this.list = list;
	}

	/**
	 * @return a {@link ArrayList} with {@link GeneralObservation} These
	 *         observations are coming from the parsing of the JSON string of
	 *         the OpenWeatherMap
	 */
	public ArrayList<MeteoObservation> getObservations() {
		ArrayList<MeteoObservation> observations = new ArrayList<MeteoObservation>();
		for (OWMObservation obs : list) {
			
			Long timestamp = new Long(obs.getDt()) * 1000;
			
			String icon = obs.getWeather().get(0).getIcon();
			String description = obs.getWeather().get(0).getDescription();
			
			//Integer minKelvinTemp = obs.getMain().getTemp_min().intValue();
			
			//Integer maxKelvinTemp = obs.getMain().getTemp_max().intValue();
			Integer observedValue = -1;
			if (icon.length() > 1)
				observedValue = Integer.parseInt(icon.substring(0, 2));
			else
				observedValue = -1;
			
			//Weather weather = new Weather( observedValue, description, (minKelvinTemp+272), (maxKelvinTemp+ 272));
			Weather weather = new Weather(observedValue, description, -1, -1);
			MeteoObservation mobs = new MeteoObservation(new Timestamp(timestamp.longValue()), observedValue);
			mobs.setMetaInformation(weather);
			observations.add(mobs);
		}
		return observations;

	}

}

class OWMObservation {
	private int dt;
	private ArrayList<OWMWeather> weather;
//	private OWMMain main;
//	private OWMWind wind;
//	private OWMRain rain;
//	private OWMClouds clouds;
	public OWMObservation(){
		this.dt= -1;
		this.weather= new ArrayList<OWMWeather>();
//		this.main= new OWMMain();
//		this.wind= new OWMWind();
//		this.rain= new OWMRain();
//		this.clouds= new OWMClouds();
	}
	
	Gson gson = new Gson();

	/**
	 * @return the timestamp (in seconds) of the observation
	 */
	public int getDt() {
		return dt;
	}

	/**
	 * @param dt
	 *            the timestamp (in seconds) of the observation
	 */
	public void setDt(int dt) {
		this.dt = dt;
	}

	public ArrayList<OWMWeather> getWeather() {
		return weather;
	}

	public void setWeather(ArrayList<OWMWeather> weather) {
		this.weather = weather;
	}

//	public OWMMain getMain() {
//		return main;
//	}
//
//	public void setMain(JsonObject main) {
//		this.main = gson.fromJson(main, OWMMain.class);
//	}
//
//	public OWMWind getWind() {
//		return wind;
//	}
//
//	public void setWind(JsonObject wind) {
//		this.wind = gson.fromJson(wind, OWMWind.class);
//	}
//
//	public OWMRain getRain() {
//		return rain;
//	}
//
//	public void setRain(JsonObject rain) {
//		this.rain = gson.fromJson(rain, OWMRain.class);
//	}
//
//	public OWMClouds getClouds() {
//		return clouds;
//	}
//
//	public void setClouds(JsonObject clouds) {
//		this.clouds = gson.fromJson(clouds, OWMClouds.class);
//	}

	

}

class OWMWeather {
	private Number id = -1;
	private String main = "";
	private String description = "";
	private String icon = "?";

	public Number getId() {
		return id;
	}

	public void setId(Number id) {
		if(id!= null)
			this.id = id;
	}

	public String getMain() {
		return main;
	}

	public void setMain(String main) {
		if(main!= null)
		this.main = main;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		if(description!= null)
		this.description = description;
	}

	public String getIcon() {
		return icon;
	}

	public void setIcon(String icon) {
		this.icon = icon;
	}
	


//class OWMWind {
//	private Number speed = -1;
//	private Number deg = -1;
//	private Number gust = -1;
//
//	public Number getGust() {
//		return gust;
//	}
//
//	public void setGust(Number gust) {
//		if(gust!= null)
//		this.gust = gust;
//	}
//
//	public Number getSpeed() {
//		return speed;
//	}
//
//	public void setSpeed(Number speed) {
//		if(speed!= null)
//		this.speed = speed;
//	}
//
//	public Number getDeg() {
//		
//		return deg;
//	}
//
//	public void setDeg(Number deg) {
//		if(deg!= null)
//		this.deg = deg;
//	}
//
//}
//
//class OWMRain {
//	private Number r1h = -1;
//	private Number r3h = -1;
//	private Number r6h = -1;
//	private Number r12h = -1;
//	private Number today = -1;
//
//	public Number getR1h() {
//		return r1h;
//	}
//
//	public void setR1h(Number r1h) {
//		if(r1h!= null)
//		this.r1h = r1h;
//	}
//
//	public Number getR3h() {
//		return r3h;
//	}
//
//	public void setR3h(Number r3h) {
//		if(r3h!= null)
//		this.r3h = r3h;
//	}
//
//	public Number getR6h() {
//		return r6h;
//	}
//
//	public void setR6h(Number r6h) {
//		if(r6h!= null)
//		this.r6h = r6h;
//	}
//
//	public Number getR12h() {
//		return r12h;
//	}
//
//	public void setR12h(Number r12h) {
//		if(r12h!= null)
//		this.r12h = r12h;
//	}
//
//	public Number getToday() {
//		return today;
//	}
//
//	public void setToday(Number today) {
//		if(today!= null)
//		this.today = today;
//	}
//
//}
//
//class OWMMain {
//	private Number temp = -1;
//	private Number pressure = -1;
//	private Number humidity = -1;
//	private Number temp_min = -1;
//	private Number temp_max = -1;
//
//	public Number getTemp() {
//		return temp;
//	}
//
//	public void setTemp(Number temp) {
//		if(temp!= null)
//			this.temp = temp;
//	}
//
//	public Number getPressure() {
//		return pressure;
//	}
//
//	public void setPressure(Number pressure) {
//		if(pressure!= null)
//			this.pressure = pressure;
//	}
//
//	public Number getHumidity() {
//		return humidity;
//	}
//
//	public void setHumidity(Number humidity) {
//		if(humidity!= null)
//		this.humidity = humidity;
//	}
//
//	public Number getTemp_min() {
//		return temp_min;
//	}
//
//	public void setTemp_min(Number temp_min) {
//		if(temp_min!= null)
//			this.temp_min = temp_min;
//	}
//
//	public Number getTemp_max() {
//		return temp_max;
//	}
//
//	public void setTemp_max(Number temp_max) {
//		if(temp_max!= null)
//			this.temp_max = temp_max;
//	}
//	
//
//}
//
//class OWMClouds {
//	private Number all = -1;
//
//	public Number getAll() {
//		return all;
//	}
//
//	public void setAll(Number all) {
//		if(all!= null)
//		this.all = all;
//	}
}

