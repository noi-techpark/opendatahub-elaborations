// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.overlay.weather;

import it.unibz.tsmodel.configuration.TSModelConfig;
import it.unibz.tsmodel.domain.MeteoObservation;

import java.util.Calendar;
import java.util.List;

public interface WeatherReader {
	public abstract List<MeteoObservation> getWeatherPredictions(TSModelConfig config);
	public List<MeteoObservation> getStoricalWeatherObservations(Calendar fromDate, TSModelConfig config);
}
