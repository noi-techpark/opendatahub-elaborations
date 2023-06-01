# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

from datetime import datetime
from unittest import TestCase

from dateutil.tz import tzutc

from pollution_connector.data_model.common import DataType, Station, Measure, Provenance


class TestDataType(TestCase):

    def test_from_odh_repr(self):
        raw_data = {
            "tdescription": "Average Speed Buses",
            "tmetadata": {},
            "tname": "Average Speed Buses",
            "ttype": "Mean",
            "tunit": "km/h",
        }

        expected_result = DataType(
            name="Average Speed Buses",
            description="Average Speed Buses",
            data_type="Mean",
            unit="km/h",
            metadata={}
        )

        data_type = DataType.from_odh_repr(raw_data)
        self.assertIsInstance(data_type, DataType)
        self.assertEqual(expected_result, data_type)


class TestStation(TestCase):

    def test_from_odh_repr(self):
        raw_data = {
            "sactive": False,
            "savailable": True,
            "scode": "A22:682:1",
            "scoordinate": {
                "x": 10,
                "y": 20,
            },
            "smetadata": {},
            "sname": "Test station",
            "sorigin": "A22",
            "stype": "TrafficSensor"
        }

        expected_result = Station(
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
        )

        station = Station.from_odh_repr(raw_data)

        self.assertIsInstance(station, Station)
        self.assertEqual(expected_result, station)


class TestMeasure(TestCase):

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

        expected_result = Measure(
            station=Station(
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

        measure = Measure.from_odh_repr(raw_data)

        self.assertIsInstance(measure, Measure)
        self.assertEqual(expected_result, measure)
