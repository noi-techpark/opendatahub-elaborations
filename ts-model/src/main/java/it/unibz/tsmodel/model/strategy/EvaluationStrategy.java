// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.model.strategy;

/**
 * @author mreinstadler
 * this is used for automated evaluation in order to 
 * set the evaluation:
 * 1) on the training set
 * 2) on the test set
 * if one of them is true the other one must be false
 *
 */
public enum EvaluationStrategy {
	/**
	 * model evaluation on the training set 
	 */
	TRAINING(true, false),
	/**
	 * model evaluation on the test set
	 */
	TEST(false, true);
	private final boolean trainingEval;
	private final boolean testEval;
	private EvaluationStrategy(boolean tr, boolean te){
		this.trainingEval = tr;
		this.testEval= te;
	}
	/**
	 * @return true if the model is evaluated on the training set
	 * in this case false for the test set
	 */
	public boolean isTrainingEval() {
		return trainingEval;
	}
	/**
	 * @return true if the model is evaluated on the test set
	 * in this case false for the training set
	 */
	public boolean isTestEval() {
		return testEval;
	}
	
	
}
