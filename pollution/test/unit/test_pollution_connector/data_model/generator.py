from __future__ import absolute_import, annotations

import random
from datetime import datetime
from typing import Optional

from pollution_connector.data_model.common import DataType, Provenance
from pollution_connector.data_model.traffic import TrafficSensorStation, TrafficMeasure


class Generator:

    @staticmethod
    def generate_traffic_station(code: Optional[str] = None) -> TrafficSensorStation:
        if code is None:
            code = f"A22:{random.randint(1, 100)}:{random.randint(1, 6)}"
        return TrafficSensorStation(
            code=code,
            active=True,
            available=True,
            coordinates={
                "x": random.randint(0, 100),
                "y": random.randint(0, 100)
            },
            metadata={},
            name=f"station {random.randint(1, 100)}",
            station_type="TrafficSensor",
            origin="A22"
        )

    @staticmethod
    def generate_datatype() -> DataType:
        name = random.choice(["Nr. Buses", "Nr. Heavy Vehicles", "Nr. Light Vehicles", "Average Speed Buses", "Average Speed Heavy Vehicles", "Average Speed Light Vehicles"])
        return DataType(
            name=name,
            description=name,
            data_type="Mean",
            unit="km/h" if "Speed" in name else "",
            metadata={}
        )

    @staticmethod
    def generate_provenance() -> Provenance:
        return Provenance(
            provenance_id="provenance_id",
            lineage="lineage",
            data_collector="data_collector",
            data_collector_version="data_collector_version"
        )

    @staticmethod
    def generate_traffic_measure(
            station: Optional[TrafficSensorStation] = None,
            data_type: Optional[DataType] = None,
            transaction_time: Optional[datetime] = None,
            valid_time: Optional[datetime] = None,
            provenance: Optional[Provenance] = None
    ) -> TrafficMeasure:

        if not station:
            station = Generator.generate_traffic_station(),
        if not data_type:
            data_type = Generator.generate_datatype()
        if not transaction_time:
            transaction_time = datetime.now()
        if not valid_time:
            valid_time = datetime.now()
        if not provenance:
            provenance = Generator.generate_provenance()

        return TrafficMeasure(
            station=station,
            data_type=data_type,
            provenance=provenance,
            period=random.randint(0, 600),
            transaction_time=transaction_time,
            valid_time=valid_time,
            value=random.randint(0, 200)
        )
