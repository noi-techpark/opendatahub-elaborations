# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import logging
from datetime import datetime
from typing import Optional, Callable, List

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from common.data_model import Station, TrafficSensorStation
from common.manager.station import StationManager
from common.manager.traffic_station import TrafficStationManager
from common.settings import ODH_MINIMUM_STARTING_DATE, DEFAULT_TIMEZONE

logger = logging.getLogger("pollution_v2.dags.common")


class StationsDAG(DAG):

    # TODO: decide if this method is necessary or should be moved to TrafficStationsDAG
    @staticmethod
    def init_date_range(min_from_date: Optional[datetime], max_to_date: Optional[datetime]):
        """
        Initializes the date range for the batch.

        :param min_from_date: Optional, if set the measures before this date are discarded.  If not specified, the
                              default will be taken from the environmental variable `ODH_MINIMUM_STARTING_DATE`.
        :param max_to_date: Optional, if set the measures after this date are discarded.
                            If not specified, the default will be the current datetime.
        :return: correctly structured dates
        """

        if min_from_date is None:
            min_from_date = ODH_MINIMUM_STARTING_DATE

        if min_from_date.tzinfo is None:
            min_from_date = DEFAULT_TIMEZONE.localize(min_from_date)

        if max_to_date is None:
            max_to_date = datetime.now(tz=DEFAULT_TIMEZONE)

        if max_to_date.tzinfo is None:
            max_to_date = DEFAULT_TIMEZONE.localize(max_to_date)

        return min_from_date, max_to_date

    @staticmethod
    def get_stations_list(manager: StationManager, **kwargs) -> List[Station]:
        """
        Returns the complete list of stations or the filtered list based on previous DAG run

        :return: list of strings containing stations list
        """
        stations = manager.get_station_list()

        if kwargs.get("dag_run") is not None:
            stations_from_prev_dag = kwargs["dag_run"].conf.get('stations_to_process')
            if stations_from_prev_dag:
                logger.info(f"{len(stations_from_prev_dag)} stations with unprocessed data from previous run, using them")
                stations = list(filter(lambda station: station.code in stations_from_prev_dag, stations))

        logger.info(f"Found {len(stations)} stations")
        return stations


class TrafficStationsDAG(StationsDAG):

    @staticmethod
    def init_date_range(min_from_date: Optional[datetime], max_to_date: Optional[datetime]):
        """
        As starting date for the batch is used the latest pollution measure available on the ODH, if no pollution
        measures are available min_from_date is used.

        :param min_from_date: Optional, if set traffic measures before this date are discarded if no pollution measures
                              are available. If not specified, the default will be taken from the environmental variable `ODH_MINIMUM_STARTING_DATE`.
        :param max_to_date: Optional, if set the traffic measure after this date are discarded.
                            If not specified, the default will be the current datetime.
        :return: correctly structured dates
        """
        return StationsDAG.init_date_range(min_from_date, max_to_date)

    @staticmethod
    def get_stations_list(manager: TrafficStationManager, filter_km_gt0: bool = False,
                          filter_indloop: bool = False, filter_famas: bool = False, **kwargs) -> List[TrafficSensorStation]:
        """
        Returns the complete list of traffic stations or the filtered list based on previous DAG run

        :return: list of strings containing stations list
        """
        res = StationsDAG.get_stations_list(manager, **kwargs)

        if filter_km_gt0:
            res = [station for station in res if station.km > 0]
            logger.info(f"Stations filtered on having km defined: {len(res)} elements")

        if filter_indloop:
            res = [station for station in res
                   if station.sensor_type is not None and station.sensor_type == 'induction_loop']
            logger.info(f"Stations filtered on sensor_type being induction_loop: {len(res)} elements")

        if filter_famas:
            res = [station for station in res
                   if station.origin is not None and station.origin != 'FAMAS-traffic']
            logger.info(f"Stations filtered on origin different from 'FAMAS-traffic': {len(res)} elements")

        return res

    @staticmethod
    def trigger_next_dag_run(manager: TrafficStationManager, originator_dag: DAG,
                             has_remaining_data: Callable[[datetime, datetime], bool],
                             batch_size: int, filter_km_gt0: bool = False, filter_indloop: bool = False,
                             filter_famas: bool = False, min_from_date = None, **kwargs):
        """
        Checks if there are still data to be processed before ending DAG runs

        :param manager: the manager to use
        :param originator_dag: the dag to trigger
        :param has_remaining_data: the function to use to check if there are still data to process
        :param batch_size: batch_size to consider
        :param filter_km_gt0: filters on km > 0 stations
        :param filter_indloop: filters on induction loop sensor type
        :param filter_famas: filters on not famas stations
        :param min_from_date: the minimum date to consider. If not specified, the default will be taken from
                              the environmental variable `ODH_MINIMUM_STARTING_DATE`.
        """

        stations = []
        all_stations = TrafficStationsDAG.get_stations_list(manager, filter_km_gt0, filter_indloop, filter_famas)
        for station in all_stations:
            if not min_from_date:
                min_from_date = ODH_MINIMUM_STARTING_DATE
            starting_date = manager.get_starting_date(manager.get_output_connector(), manager.get_input_connector(),
                                                      [station], min_from_date, batch_size, False)
            input_data_types = manager.get_input_data_types()
            ending_date = manager.get_starting_date(manager.get_input_connector(), None, [station], min_from_date,
                                                    batch_size, False, output_data_types=input_data_types)
            if starting_date is None:
                logger.info(f"Nothing to process on {station.code}, not forwarded to next execution")
            else:
                logger.info(f"Check if [{station.code}] has more data on dates ranging from [{starting_date}] to [{ending_date}]")
                if has_remaining_data(starting_date, ending_date):
                    logger.info(f"Forwarding station {station.code} to next execution")
                    stations.append(station.code)

        # True if on ODH there are lots of data to be processed (e.g. new station with old unprocessed data)
        run_again = len(stations) > 0

        logger.info(f"{'S' if run_again else 'NOT s'}tarting another self-triggered run as {len(stations)} "
                    f"stations have still unprocessed data")

        if run_again:
            TriggerDagRunOperator(
                task_id="run_again_the_dag",
                trigger_dag_id=originator_dag.dag_id,
                dag=originator_dag,
                conf={'stations_to_process': stations}
            ).execute(kwargs)
