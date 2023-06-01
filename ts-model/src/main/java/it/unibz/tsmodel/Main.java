// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel;

import org.springframework.context.ApplicationContext;

/**
 * @author mreinstadler
 * main class of the ts-analyis
 *
 */
public class Main {

	
	/**
	 * main method always alive
	 * @param args
	 */
	public static ApplicationContext main(String[] args) {
		Main m = new Main();
		ApplicationContextLoader context = new  ApplicationContextLoader();
		context.load(m, "META-INF/spring/applicationContext.xml");
		return context.getApplicationContext();
	}

}
