// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.model.strategy;


/**
 * @author mreinstadler
 * this is used to define the chosen lag strategy
 * for the model building process. Either a simple
 * strategy is used (e.g for hourly periodicity 24 lag 
 * variables, which corresponds to 1 whole day) or 
 * a more refined strategy.
 *
 */
public enum LagStrategy {
	SIMPLE_LAG(1,24), EXTENDED_LAG(1,168);
	private final int minLag;
	private final int maxLag;
	private LagStrategy(int minLag, int maxLag) {
		this.minLag = minLag;
		this.maxLag = maxLag;
	}
	/**
	 * @return the minimum number of lag variables for 
	 * this strategy
	 */
	public int getMinLag() {
		return minLag;
	}
	/**
	 * @return the maximum number of lag variables
	 * for this strategy
	 */
	public int getMaxLag() {
		return maxLag;
	}
	

}
