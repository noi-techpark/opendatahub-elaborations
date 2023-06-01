// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.model.strategy;

import weka.classifiers.Classifier;
import weka.classifiers.functions.LinearRegression;
import weka.classifiers.rules.M5Rules;
import weka.classifiers.timeseries.WekaForecaster;

/**
 * @author mreinstadler
 * the {@link WekaForecaster} {@link Classifier} to be used
 * to train the model. Actually we consider only M5Rule and linear
 * regression, but there could be any other Classifier in this 
 * enmumeration.
 *
 */
public enum BaseLearnerStrategy{
	
	M5RULE(new M5Rules()),
	LINREG(new LinearRegression());
	private final Classifier classif;
	private BaseLearnerStrategy(Classifier classif){
		this.classif = classif;
	}
	
	/**
	 * @return the {@link Classifier} used to train 
	 * the model
	 */
	public Classifier getClassifierStrategy(){
		return this.classif;
	}

}
