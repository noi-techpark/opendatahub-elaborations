# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 15:07:03 2023

@author: nicola
"""

import sqlite3
import holidays
import datetime
import pandas as pd


class Input:
    def __init__(self, day, db_path):
        self.day = datetime.datetime.strptime(day, '%Y-%m-%d').date()
        self.chilometriche = self.get_km(db_path)
        self.history = self.get_history(db_path)
        self.raw_data = self.get_raw_data(db_path)
        self.station_list = self.get_stations()

    def get_history(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM history"
        cursor.execute(query)
        hist = cursor.fetchall()
        conn.close()
        hist = pd.DataFrame(hist)
        hist.columns = ['date', 'station', 'lane', 'total_traffic']
        hist['station'] = hist['station'].astype(int)
        hist['date'] = pd.to_datetime(hist['date'])
        hist = hist[hist['date'].dt.month == self.day.month]

        # QUESTO RALLENTA PARECCHIO IL CODICE #################################
        hist['daytype'] = hist['date'].apply(get_daytype)
        #######################################################################

        hist = hist[hist['daytype'] == get_daytype(self.day)]
        return hist

    def get_raw_data(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM ODH_raw_data WHERE time LIKE '{self.day}%'"
        cursor.execute(query)
        raw_data = cursor.fetchall()
        conn.close()
        raw_data = pd.DataFrame(raw_data)
        raw_data.columns = ['time', 'value', 'station_code', 'variable']
        raw_data[['domain', 'station', 'lane']] = raw_data['station_code'].str.split(':', expand=True)
        raw_data['direction'] = raw_data['lane'].map(
            {'1': 'NORD', '2': 'NORD', '3': 'SUD', '4': 'SUD', '5': 'NORD', '6': 'SUD'})
        raw_data['station'] = raw_data['station'].astype(int)
        raw_data['km'] = raw_data['station'].map(self.chilometriche)
        return raw_data

    def get_km(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM km"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        km = dict(data)
        return km

    def get_stations(self):
        return self.raw_data[['station', 'direction']].drop_duplicates()


def get_daytype(date):
    if date.weekday() >= 5 or date in holidays.Italy():
        tipo = 'Festivo'
    else:
        tipo = 'Feriale'
    return tipo
