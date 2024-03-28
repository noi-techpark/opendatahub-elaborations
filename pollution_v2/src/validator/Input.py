# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import holidays
import datetime
import pandas as pd

class Input:
    def __init__(self, day, raw_data, history, km, station_type):
        self.day = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        self.chilometriche = km
        self.station_type = station_type
        self.history = self.get_history(history)
        self.raw_data = self.get_raw_data(raw_data)
        self.station_list = self.get_stations()

    def get_history(self, history):
        """
        History pre-elaborations: check column types and add daytype column
        - Parameters:
        history : dataframe ['date', 'station_code', 'total_traffic']
        - Returns:
        history : dataframe ['date', 'domain', 'station', 'lane', 'total_traffic', 'daytype']
        """
        history[['domain', 'station', 'lane']] = history['station_code'].str.split(':', expand=True)
        history['station'] = history['station'].astype(int)
        history['date'] = pd.to_datetime(history['date'])
        history = history[history['date'].dt.month == self.day.month]
        history['daytype'] = history['date'].apply(get_daytype)
        hist = history[history['daytype'] == get_daytype(self.day)]
        return hist

    def get_raw_data(self, raw_data):
        """
        Raw Data pre-elaborations: check column types and add direction and km columns
        - Parameters:
        raw_data : dataframe ['time', 'value', 'station_code', 'variable']
        - Returns:
        raw_data : dataframe ['time', 'value', 'domain', 'station', 'lane', 'variable', 'direction', 'km']
        """
        raw_data[['domain', 'station', 'lane']] = raw_data['station_code'].str.split(':', expand=True)
        raw_data['direction'] = raw_data['lane'].map({'1': 'NORD', '2': 'NORD', '3': 'SUD', '4': 'SUD', '5': 'NORD', '6': 'SUD'})
        raw_data['station'] = raw_data['station'].astype(int)
        raw_data['km'] = raw_data['station'].map(self.chilometriche.T.to_dict('list'))
        return raw_data

    def get_stations(self):
        """
        Get station list from raw data
        - Parameters:
        - Returns:
        station_list : list
        """
        station_list = self.raw_data[['station', 'direction']].drop_duplicates()
        return station_list

def get_daytype(date):
    if date.weekday() >= 5 or date in holidays.Italy():
        tipo = 'Festivo'
    else:
        tipo = 'Feriale'
    return tipo
