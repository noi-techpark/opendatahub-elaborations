# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import logging
from datetime import datetime, timedelta
from typing import List

from common.cache.common import TrafficManagerClass
from common.connector.common import ODHBaseConnector
from common.data_model import TrafficSensorStation
from common.data_model.entry import GenericEntry
from common.data_model.history import HistoryMeasureCollection
from common.data_model.traffic import TrafficMeasureCollection
from common.data_model.validation import ValidationMeasure, ValidationMeasureCollection, ValidationEntry
from common.manager.traffic_station import TrafficStationManager
from common.data_model.common import DataType, MeasureCollection
from common.settings import DEFAULT_TIMEZONE
from validator.model.validation_model import ValidationModel

logger = logging.getLogger("pollution_v2.validator.manager.validation")


class ValidationManager(TrafficStationManager):
    """
    Manager in charge of executing validation.
    """

    def _get_manager_code(self) -> str:
        return TrafficManagerClass.VALIDATION.name

    def get_output_connector(self) -> ODHBaseConnector:
        return self._connector_collector.validation

    def get_input_connector(self) -> ODHBaseConnector:
        return self._connector_collector.traffic

    def _download_history_data(self,
                               from_date: datetime,
                               to_date: datetime
                               ) -> HistoryMeasureCollection:
        """
        Download history data measures in the given interval.

        :param from_date: History measures before this date are discarded if there isn't any latest measure available.
        :param to_date: History measure after this date are discarded.
        :return: The resulting HistoryMeasureCollection containing the traffic data.
        """

        # set time to midnight otherwise you'll miss today's value
        from_date = DEFAULT_TIMEZONE.localize(datetime.combine(from_date, datetime.min.time()))

        measures = []
        from_date_on_month = from_date.replace(day=1)
        to_date_on_month = datetime(to_date.year, to_date.month + 1, 1) + timedelta(days=-1)
        if to_date_on_month.tzinfo is None:
            to_date_on_month = DEFAULT_TIMEZONE.localize(to_date_on_month)

        for i in range(0, 4):
            from_date_to_use = from_date_on_month.replace(year=from_date_on_month.year-i)
            to_date_to_use = min(to_date_on_month.replace(year=to_date_on_month.year-i), to_date)
            measures.extend(self._connector_collector.history.get_measures(from_date=from_date_to_use,
                                                                           to_date=to_date_to_use))

        return HistoryMeasureCollection(measures=measures)

    def _download_data_and_compute(self, start_date: datetime, to_date: datetime,
                                   stations: List[TrafficSensorStation]) -> List[GenericEntry]:

        history_data = []
        traffic_data = []
        try:
            # no station as for history every station is needed
            history_data = self._download_history_data(start_date, to_date)
            # no station as parameter as validation needs data from all stations
            traffic_data = self._download_traffic_data(start_date, to_date, stations)
        except Exception as e:
            logger.exception(
                f"Unable to download history and traffic data "
                f"in the interval [{start_date.isoformat()}] - [{to_date.isoformat()}]",
                exc_info=e)

        if history_data and traffic_data:
            model = ValidationModel()
            return model.compute_data(history_data, TrafficMeasureCollection(traffic_data),
                                      stations)

        return []

    def _get_data_types(self) -> List[DataType]:
        return ValidationMeasure.get_data_types()

    def _build_from_entries(self, input_entries: List[ValidationEntry]) -> MeasureCollection:
        return ValidationMeasureCollection.build_from_entries(input_entries, self._provenance)
