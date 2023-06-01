# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from datetime import datetime
from typing import List
from unittest import TestCase

from dateutil.tz import tzutc

from pollution_connector.data_model.common import DataType, VehicleClass, Provenance
from pollution_connector.data_model.traffic import TrafficSensorStation, TrafficMeasure, TrafficMeasureCollection
from test.unit.test_pollution_connector.data_model.generator import Generator


class TestTrafficSensorStation(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.station = TrafficSensorStation(
            code="A22:12:1",
            active=True,
            available=True,
            coordinates={
                "x": 1,
                "y": 1
            },
            metadata={},
            name="station 12",
            station_type="TrafficSensor",
            origin="A22"
        )

    def test_split_station_code(self):
        self.assertEqual(("A22", 12, 1), self.station.split_station_code())

    def test_id_strada(self):
        self.assertEqual("A22", self.station.id_strada)

    def test_id_stazione(self):
        self.assertEqual(12, self.station.id_stazione)

    def test_id_corsia(self):
        self.assertEqual(1, self.station.id_corsia)


class TestTrafficMeasure(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.station = TrafficSensorStation(
            code="A22:12:1",
            active=True,
            available=True,
            coordinates={
                "x": 1,
                "y": 1
            },
            metadata={},
            name="station 12",
            station_type="TrafficSensor",
            origin="A22"
        )

        self.nr_busses_data_type = DataType(
            name="Nr. Buses",
            description="Nr. Buses",
            data_type="Mean",
            unit="",
            metadata={}
        )

        self.speed_busses_data_type = DataType(
            name="Average Speed Buses",
            description="Average Speed Buses",
            data_type="Mean",
            unit="km/h",
            metadata={}
        )

        self.nr_heavy_data_type = DataType(
            name="Nr. Heavy Vehicles",
            description="Nr. Heavy Vehicles",
            data_type="Mean",
            unit="",
            metadata={}
        )

        self.speed_heavy_data_type = DataType(
            name="Average Speed Heavy Vehicles",
            description="Average Speed Heavy Vehicles",
            data_type="Mean",
            unit="km/h",
            metadata={}
        )

        self.nr_light_data_type = DataType(
            name="Nr. Light Vehicles",
            description="Nr. Light Vehicles",
            data_type="Mean",
            unit="",
            metadata={}
        )

        self.speed_light_data_type = DataType(
            name="Average Speed Light Vehicles",
            description="Average Speed Light Vehicles",
            data_type="Mean",
            unit="km/h",
            metadata={}
        )

        self.heavy_speed_measure = Generator.generate_traffic_measure(self.station, self.speed_heavy_data_type)
        self.light_speed_measure = Generator.generate_traffic_measure(self.station, self.speed_light_data_type)
        self.busses_speed_measure = Generator.generate_traffic_measure(self.station, self.speed_busses_data_type)
        self.heavy_number_measure = Generator.generate_traffic_measure(self.station, self.nr_heavy_data_type)
        self.light_number_measure = Generator.generate_traffic_measure(self.station, self.nr_light_data_type)
        self.busses_number_measure = Generator.generate_traffic_measure(self.station, self.nr_busses_data_type)

    def test_vehicle_class(self):
        self.assertEqual(self.heavy_speed_measure.vehicle_class, VehicleClass.HEAVY_VEHICLES)
        self.assertEqual(self.heavy_number_measure.vehicle_class, VehicleClass.HEAVY_VEHICLES)
        self.assertEqual(self.light_number_measure.vehicle_class, VehicleClass.LIGHT_VEHICLES)
        self.assertEqual(self.light_speed_measure.vehicle_class, VehicleClass.LIGHT_VEHICLES)
        self.assertEqual(self.busses_number_measure.vehicle_class, VehicleClass.BUSES)
        self.assertEqual(self.busses_speed_measure.vehicle_class, VehicleClass.BUSES)

    def test_is_vehicle_counting_measure(self):
        self.assertTrue(self.heavy_number_measure.is_vehicle_counting_measure)
        self.assertTrue(self.light_number_measure.is_vehicle_counting_measure)
        self.assertTrue(self.busses_number_measure.is_vehicle_counting_measure)
        self.assertFalse(self.heavy_speed_measure.is_vehicle_counting_measure)
        self.assertFalse(self.light_speed_measure.is_vehicle_counting_measure)
        self.assertFalse(self.busses_speed_measure.is_vehicle_counting_measure)

    def test_is_average_speed_measure_measure(self):
        self.assertFalse(self.heavy_number_measure.is_average_speed_measure)
        self.assertFalse(self.light_number_measure.is_average_speed_measure)
        self.assertFalse(self.busses_number_measure.is_average_speed_measure)
        self.assertTrue(self.heavy_speed_measure.is_average_speed_measure)
        self.assertTrue(self.light_speed_measure.is_average_speed_measure)
        self.assertTrue(self.busses_speed_measure.is_average_speed_measure)

    def test_from_odh_repr(self):
        raw_data = {
            "tdescription": "Average Speed Buses",
            "tmetadata": {},
            "tname": "Average Speed Buses",
            "ttype": "Mean",
            "tunit": "km/h",
            "mperiod": 600,
            "mtransactiontime": "2019-12-13 12:08:14.309+0000",
            "mvalidtime": "2020-02-12 00:00:00.000+0000",
            "mvalue": 80,
            "prlineage": "A22",
            "prname": "dc-trafficelaborations-a22",
            "prversion": "1.0.2",
            "sactive": False,
            "savailable": True,
            "scode": "A22:682:1",
            "scoordinate": {
                "x": 10,
                "y": 20
            },
            "smetadata": {},
            "sname": "Test station",
            "sorigin": "A22",
            "stype": "TrafficSensor"
        }

        expected_result = TrafficMeasure(
            station=TrafficSensorStation(
                code="A22:682:1",
                active=False,
                available=True,
                coordinates={
                    "x": 10,
                    "y": 20,
                },
                metadata={},
                name="Test station",
                station_type="TrafficSensor",
                origin="A22"
            ),
            data_type=DataType(
                name="Average Speed Buses",
                description="Average Speed Buses",
                data_type="Mean",
                unit="km/h",
                metadata={}
            ),
            provenance=Provenance(
                provenance_id=None,
                lineage="A22",
                data_collector="dc-trafficelaborations-a22",
                data_collector_version="1.0.2"
            ),
            period=600,
            transaction_time=datetime(2019, 12, 13, 12, 8, 14, 309000, tzinfo=tzutc()),
            valid_time=datetime(2020, 2, 12, 0, 0, tzinfo=tzutc()),
            value=80
        )

        measure = TrafficMeasure.from_odh_repr(raw_data)

        self.assertIsInstance(measure, TrafficMeasure)
        self.assertEqual(expected_result, measure)


class TestTrafficMeasureCollection(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.station = TrafficSensorStation(
            code="A22:12:1",
            active=True,
            available=True,
            coordinates={
                "x": 1,
                "y": 1
            },
            metadata={},
            name="station 12",
            station_type="TrafficSensor",
            origin="A22"
        )

        self.nr_busses_data_type = DataType(
            name="Nr. Buses",
            description="Nr. Buses",
            data_type="Mean",
            unit="",
            metadata={}
        )

        self.speed_busses_data_type = DataType(
            name="Average Speed Buses",
            description="Average Speed Buses",
            data_type="Mean",
            unit="km/h",
            metadata={}
        )

        self.nr_heavy_data_type = DataType(
            name="Nr. Heavy Vehicles",
            description="Nr. Heavy Vehicles",
            data_type="Mean",
            unit="",
            metadata={}
        )

        self.speed_heavy_data_type = DataType(
            name="Average Speed Heavy Vehicles",
            description="Average Speed Heavy Vehicles",
            data_type="Mean",
            unit="km/h",
            metadata={}
        )

        self.nr_light_data_type = DataType(
            name="Nr. Light Vehicles",
            description="Nr. Light Vehicles",
            data_type="Mean",
            unit="",
            metadata={}
        )

        self.speed_light_data_type = DataType(
            name="Average Speed Light Vehicles",
            description="Average Speed Light Vehicles",
            data_type="Mean",
            unit="km/h",
            metadata={}
        )

    def _generate_traffic_measures(self, number: int) -> List[TrafficMeasure]:
        result = []
        for _ in range(number):
            station = Generator.generate_traffic_station()
            valid_time = datetime.now()
            transaction_time = datetime.now()
            result.append(Generator.generate_traffic_measure(station, self.speed_busses_data_type, transaction_time, valid_time))
            result.append(Generator.generate_traffic_measure(station, self.speed_heavy_data_type, transaction_time, valid_time))
            result.append(Generator.generate_traffic_measure(station, self.speed_light_data_type, transaction_time, valid_time))
            result.append(Generator.generate_traffic_measure(station, self.nr_busses_data_type, transaction_time, valid_time))
            result.append(Generator.generate_traffic_measure(station, self.nr_light_data_type, transaction_time, valid_time))
            result.append(Generator.generate_traffic_measure(station, self.nr_heavy_data_type, transaction_time, valid_time))

        return result

    def test_get_traffic_entries(self):

        measures = self._generate_traffic_measures(10)
        collection = TrafficMeasureCollection()
        collection.with_measures(measures)

        entries = list(collection.get_traffic_entries())

        self.assertEqual(30, len(entries))
        for entry in entries:
            self.assertIsNotNone(entry.average_speed)
            self.assertIsNotNone(entry.nr_of_vehicles)

    def test_duplicated_entry(self):
        station = Generator.generate_traffic_station()
        valid_time = datetime.now()
        transaction_time = datetime.now()
        measures = [
            Generator.generate_traffic_measure(station, self.speed_busses_data_type, transaction_time, valid_time),
            Generator.generate_traffic_measure(station, self.speed_busses_data_type, transaction_time, valid_time),
        ]
        collection = TrafficMeasureCollection()
        collection.with_measures(measures)

        with self.assertRaises(ValueError):
            list(collection.get_traffic_entries())
