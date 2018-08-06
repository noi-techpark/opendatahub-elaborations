package it.unibz.tsmodel.parser.filter;

import it.unibz.tsmodel.domain.ObservationPeriodicity;
import it.unibz.tsmodel.domain.ParkingObservation;

import java.util.Calendar;
import java.util.List;

public class TSManualInterpolFilter implements TSInterpolationFilter {

	@Override
	public void filterTimeseries(List<ParkingObservation> parkingObservations, ObservationPeriodicity periodicity) {
		if(parkingObservations.size()<6)
			return;
		int index=11;
		while (index < parkingObservations.size()) {
			Calendar cal = Calendar.getInstance();
			cal.setTime(parkingObservations.get(index).getTimestamp());
			int p1 = parkingObservations.get(index - 11).getObservedValue();
			int p2 = parkingObservations.get(index - 10).getObservedValue();
			int p3 = parkingObservations.get(index - 9).getObservedValue();
			int p4 = parkingObservations.get(index - 8).getObservedValue();
			int p5 = parkingObservations.get(index - 7).getObservedValue();
			int p6 = parkingObservations.get(index - 6).getObservedValue();
			int p7 = parkingObservations.get(index - 5).getObservedValue();
			int p8 = parkingObservations.get(index - 4).getObservedValue();
			int p9 = parkingObservations.get(index - 3).getObservedValue();
			int p10 = parkingObservations.get(index -2).getObservedValue();
			int p11 = parkingObservations.get(index -1).getObservedValue();
			int p12= parkingObservations.get(index).getObservedValue();
			if (p12==p11 && p11==p10 && p10==p9&& p9==p8&& p8==p7&& p7==p6
					&& p6==p5&& p5==p4&& p4==p3&& p3==p2&& p2==p1)
				index = interpolateFaultyValues(parkingObservations, index -11, periodicity);
			index++;
		}		
	}
	
	/**
	 * @param parkingObservations the list of {@link ParkingObservation}
	 * @param startindex the index in the list of {@link ParkingObservation} to start resetting
	 * the faulty values
	 * @param periodicity the {@link ObservationPeriodicity} of the time-series
	 * @return the index of the first element after the faulty values 
	 */
	private int interpolateFaultyValues(List<ParkingObservation> parkingObservations, 
			int startindex, ObservationPeriodicity periodicity){
		int weekAgoIndex = 168 *(60/periodicity.minutes());
		int dayAgo = 24 *(60/periodicity.minutes());
		int v1= parkingObservations.get(startindex).getObservedValue();
		if((startindex- weekAgoIndex )>=0){
			
			while(startindex< parkingObservations.size() && parkingObservations.
					get(startindex).getObservedValue()==v1){
				int value = parkingObservations.
						get(startindex-weekAgoIndex).getObservedValue();
				if(value >0)
					parkingObservations.get(startindex).setObservedValue(value);
				else{
					value = parkingObservations.
							get(startindex-dayAgo).getObservedValue();
					if(value >0)
						parkingObservations.get(startindex).setObservedValue(value);
				}
				startindex++;
			}
		}
		else if((startindex- dayAgo)>=0){
			while(startindex< parkingObservations.size() && parkingObservations.
					get(startindex).getObservedValue()==v1){
				parkingObservations.get(startindex).setObservedValue(parkingObservations.
						get(startindex-dayAgo).getObservedValue());
				startindex++;
			}
		}
		else{
			while(startindex< parkingObservations.size() && parkingObservations.
					get(startindex).getObservedValue()==v1){
				parkingObservations.get(startindex).setObservedValue(-1);
				startindex++;
			}
		}
		startindex--;
		return startindex;
			
	}

}
