// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.parser.filter;

import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;

import java.util.Calendar;
import java.util.List;

public class TSAutoInterpolFilter implements TSInterpolationFilter{

	@Override
	public void filterTimeseries(List<ParkingObservation> parkingObservations, 
			ObservationPeriodicity periodicity) {
		if(parkingObservations.size()<6)
			return;
		int index=5;
		while (index < parkingObservations.size()) {
			Calendar cal = Calendar.getInstance();
			cal.setTime(parkingObservations.get(index).getTimestamp());
			int p1 = parkingObservations.get(index - 5).getObservedValue();
			int p2 = parkingObservations.get(index - 4).getObservedValue();
			int p3 = parkingObservations.get(index - 3).getObservedValue();
			int p4 = parkingObservations.get(index - 2).getObservedValue();
			int p5 = parkingObservations.get(index - 1).getObservedValue();
			int p6 = parkingObservations.get(index).getObservedValue();
			if (cal.get(Calendar.HOUR_OF_DAY) > 5 && p6 == p1 && p6 == p2
					&& p6 == p3 && p6 == p4 && p6 == p5)
				index = resetFoultyValues(parkingObservations, index - 5);
			index++;
		}		
	}
	/**
	 * @param parkingObservations the list of {@link ParkingObservation}
	 * @param startindex the index in the list of {@link ParkingObservation} to start resetting
	 * the faulty values
	 * @return the index of the first element after the faulty values 
	 */
	private int resetFoultyValues(List<ParkingObservation> parkingObservations, int startindex){
		int v1= parkingObservations.get(startindex).getObservedValue();
		while(startindex< parkingObservations.size() && parkingObservations.get(startindex).getObservedValue()==v1){
			parkingObservations.get(startindex).setObservedValue(-1);
			startindex++;
		}
		startindex--;
		return startindex;
			
	}

}
