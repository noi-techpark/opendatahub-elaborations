package it.bz.odh.elaborations.services;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.OptionalDouble;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.apache.commons.lang3.time.DateUtils;
import org.springframework.stereotype.Service;

import it.bz.idm.bdp.dto.SimpleRecordDto;

@Service
public class ElaborationService {

    private static final int PERIOD = 3600;
    private static final long HOUR = 1000 * 3600l;
    public static final int MIN_AMOUNT_OF_DATA_POINTS = 16;

    public List<SimpleRecordDto> calcAverage(Long now, List<SimpleRecordDto> rawData, int timeReference) {
        List<SimpleRecordDto> elaborations = new ArrayList<>();
        if (rawData == null || rawData.isEmpty()) {
            return elaborations;
        }

        Collections.sort(rawData);

        Date maxCalcDate = new Date(rawData.get(rawData.size() - 1).getTimestamp());
        if (now < maxCalcDate.getTime() + HOUR)
            maxCalcDate = new Date(now);
        Long maxCalc = DateUtils.truncate(maxCalcDate, timeReference).getTime();

        long intervalStart = DateUtils.truncate((new Date(rawData.get(0).getTimestamp())), timeReference).getTime();
        long intervalEnd = intervalStart + HOUR;
        Long[] intervals = new Long[] { intervalStart, intervalEnd };

        while (intervals[1] <= maxCalc) {
            Stream<SimpleRecordDto> filteredStream = rawData
                .stream()
                .filter(x -> x.getTimestamp() > intervals[0] && x.getTimestamp() <= intervals[1]);

            List<SimpleRecordDto> recordsPerHour = filteredStream.collect(Collectors.toList());

            if (recordsPerHour.size() >= MIN_AMOUNT_OF_DATA_POINTS) {
                OptionalDouble average = recordsPerHour
                    .stream()
                    .mapToDouble(x -> new Double(x.getValue().toString()))
                    .average();

                if (average.isPresent())
                    elaborations.add(new SimpleRecordDto(intervals[1], average.getAsDouble(), PERIOD));
            }

            intervals[0] += HOUR;
            intervals[1] += HOUR;
        }
        return elaborations;
    }

}
