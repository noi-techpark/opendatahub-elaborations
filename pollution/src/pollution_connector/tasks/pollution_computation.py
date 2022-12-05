from __future__ import absolute_import, annotations

import logging
from datetime import datetime, timedelta
from typing import Optional, List

from pollution_connector.celery_configuration.celery_app import app
from pollution_connector.connector.collector import ConnectorCollector
from pollution_connector.data_model.common import Provenance
from pollution_connector.data_model.pollution import PollutionMeasure, PollutionMeasureCollection, PollutionEntry
from pollution_connector.data_model.traffic import TrafficMeasureCollection, TrafficSensorStation, TrafficMeasure
from pollution_connector.pollution_computation_model.pollution_computation_model import PollutionComputationModel
from pollution_connector.settings import DEFAULT_TIMEZONE, ODH_MINIMUM_STARTING_DATE, PROVENANCE_ID, PROVENANCE_LINEAGE, \
    PROVENANCE_NAME, PROVENANCE_VERSION

logger = logging.getLogger("pollution_connector.tasks.pollution_computation")


@app.task
def compute_pollution_data(min_from_date: Optional[datetime] = None,
                           max_to_date: Optional[datetime] = None
                           ) -> None:
    """
    Start the computation of a batch of pollution data measures. As starting date for the batch is used the latest
    pollution measure available on the ODH, if no pollution measures are available min_from_date is used.

    :param min_from_date: Optional, if set traffic measures before this date are discarded if no pollution measures are available.
                          If not specified, the default will be taken from the environmental variable `ODH_MINIMUM_STARTING_DATE`.
    :param max_to_date: Optional, if set the traffic measure after this date are discarded.
                        If not specified, the default will be the current datetime.
    """
    if min_from_date is None:
        min_from_date = ODH_MINIMUM_STARTING_DATE

    if max_to_date is None:
        max_to_date = datetime.now(tz=DEFAULT_TIMEZONE)

    collector_connector = ConnectorCollector.build_from_env()
    provenance = Provenance(PROVENANCE_ID, PROVENANCE_LINEAGE, PROVENANCE_NAME, PROVENANCE_VERSION)
    manager = PollutionComputationManager(collector_connector, provenance)
    manager.run_computation_and_upload_results(min_from_date, max_to_date)


class PollutionComputationManager:

    def __init__(self, connector_collector: ConnectorCollector, provenance: Provenance):
        self._connector_collector = connector_collector
        self._provenance = provenance
        self._create_data_types = True
        self._traffic_stations: List[TrafficSensorStation] = []

    def _traffic_stations_from_cache(self) -> List[TrafficSensorStation]:
        if len(self._traffic_stations) == 0:
            logger.info("Retrieving station list from ODH")
            self._traffic_stations = self._get_station_list()
        return self._traffic_stations

    def _get_station_list(self) -> List[TrafficSensorStation]:
        """
        Retrieve the list of all the available stations.
        """
        return self._connector_collector.traffic.get_station_list()

    def _get_latest_pollution_measure(self, traffic_station: TrafficSensorStation) -> Optional[PollutionMeasure]:
        """
        Retrieve the latest pollution measure for a given station. It will be the oldest one among all the measure types
        (CO-emissions, CO2-emissions, ...) even though should be the same for all the types.

        :param traffic_station: The station for which retrieve the latest pollution measure.
        :return: The latest pollution measure for a given station.
        """
        latest_pollution_measures = self._connector_collector.pollution.get_latest_measures(traffic_station)
        if latest_pollution_measures:
            self._create_data_types = False
            latest_pollution_measures.sort(key=lambda x: x.valid_time)
            return latest_pollution_measures[0]

    def _download_traffic_data(self,
                               min_from_date: datetime,
                               max_to_date: datetime
                               ) -> TrafficMeasureCollection:
        """
        Download traffic data measures. As starting date for the batch is used the latest pollution measure available
        on the ODH, if there isn't any, the min_from_date is used.

        :param min_from_date: Traffic measures before this date are discarded if there isn't any latest pollution measure available.
        :param max_to_date: Traffic measure after this date are discarded.
        :return: The resulting TrafficMeasureCollection containing the traffic data.
        """
        traffic_measures: List[TrafficMeasure] = []
        for traffic_station in self._traffic_stations_from_cache():
            latest_pollution_measure = self._get_latest_pollution_measure(traffic_station)
            if latest_pollution_measure is None:
                from_date = min_from_date  # If there isn't any latest pollution measure available, the min_from_date is used as starting date for the batch
            else:
                from_date = latest_pollution_measure.valid_time

            if from_date.tzinfo is None:
                from_date = DEFAULT_TIMEZONE.localize(from_date)

            if from_date.microsecond:
                from_date = from_date.replace(microsecond=0)

            if max_to_date.tzinfo is None:
                max_to_date = DEFAULT_TIMEZONE.localize(max_to_date)

            if max_to_date > from_date:
                try:
                    traffic_measures.extend(self._connector_collector.traffic.get_measures(from_date=from_date, to_date=max_to_date, station=traffic_station))
                except Exception as e:  # If there is an error log it and go to the next station
                    logger.exception(f"Exception in getting data for traffic station [{traffic_station}] from ODH", exc_info=e)

        return TrafficMeasureCollection(measures=traffic_measures)

    @staticmethod
    def _compute_pollution_data(traffic_data: TrafficMeasureCollection) -> List[PollutionEntry]:
        """
        Compute the pollution data given the traffic data.

        :param traffic_data: The traffic data.
        :return: The pollution entries.
        """
        model = PollutionComputationModel()
        return model.compute_pollution_data(traffic_data)

    def _upload_pollution_data(self, pollution_entries: List[PollutionEntry]) -> None:  # If a data is already present it will be not overridden and data before the last measures are not accepted by the ODH
        """
        Upload the pollution data on ODH.

        :param pollution_entries: The pollution entries.
        """
        if not self._provenance.provenance_id:
            self._provenance.provenance_id = self._connector_collector.pollution.post_provenance(self._provenance)

        if self._create_data_types:
            self._connector_collector.pollution.post_data_types(PollutionMeasure.get_pollution_data_types(), self._provenance)

        pollution_data = PollutionMeasureCollection.build_from_pollution_entries(pollution_entries, self._provenance)

        self._connector_collector.pollution.post_measures(pollution_data.measures)

    def run_computation_and_upload_results(self,
                                           min_from_date: datetime,
                                           max_to_date: datetime
                                           ) -> None:
        """
        Start the computation of a batch of pollution data measures. As starting date for the batch is used the latest
        pollution measure available on the ODH, if no pollution measures are available min_from_date is used.

        :param min_from_date: Traffic measures before this date are discarded if no pollution measures are available.
        :param max_to_date: Traffic measure after this date are discarded.
        """

        if min_from_date.tzinfo is None:
            min_from_date = DEFAULT_TIMEZONE.localize(min_from_date)

        if max_to_date.tzinfo is None:
            max_to_date = DEFAULT_TIMEZONE.localize(max_to_date)

        computation_start_dt = datetime.now()

        start_date = min_from_date
        to_date = start_date

        while start_date < max_to_date:
            to_date = to_date + timedelta(days=30)
            if to_date > max_to_date:
                to_date = max_to_date

            logger.info(f"computing computation for interval [{start_date.isoformat()}] - [{to_date.isoformat()}]")
            traffic_data = self._download_traffic_data(start_date, to_date)
            pollution_entries = self._compute_pollution_data(traffic_data)
            self._upload_pollution_data(pollution_entries)

            logger.info(f"Computed [{len(pollution_entries)}] for interval [{start_date.isoformat()}] - [{to_date.isoformat()}]")

            start_date = to_date

        computation_end_dt = datetime.now()
        logger.info(f"Completed computation in [{(computation_end_dt - computation_start_dt).seconds}]")
