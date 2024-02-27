#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
import numpy as np
import yaml
import matplotlib.pyplot as plt


class Parametri:
    def __init__(self, file_yaml):
        with open(file_yaml, 'r') as file:
            self.parametri = yaml.safe_load(file)

    def database(self, param):
        return self.parametri['db_path'][param]

    def layer1(self, param):
        return self.parametri['Layer1'][param]

    def layer1_1(self, param):
        return self.parametri['Layer1_1'][param]

    def layer2(self, param):
        return self.parametri['Layer2'][param]


class Dominio:
    def __init__(self):
        self.station_list = []
        self.layer1_not_valid = []
        self.layer1_1_not_valid = []
        self.layer2_not_valid = []
        self.layer3_not_valid = []

    def add_station(self, station):
        self.station_list.append(station)

    def layer1_not_valid_station(self, station):
        self.layer1_not_valid.append(station)

    def layer1_1_not_valid_station(self, station):
        self.layer1_1_not_valid.append(station)

    def layer2_not_valid_station(self, station):
        self.layer2_not_valid.append(station)

    def layer3_not_valid_station(self, station):
        self.layer3_not_valid.append(station)

    def zscore_statistics(self):
        zscore_list = [stazione.zscore for stazione in self.station_list]
        media_zscore = np.mean(zscore_list)
        deviazione_std_zscore = np.std(zscore_list)
        self.stats1_1 = {'mean': media_zscore, 'std': deviazione_std_zscore}


class Station:
    # Inizializza l'oggetto stazione con le caratteristiche identificative
    # e i dati giornalieri.
    def __init__(self, data, history, ID, direction, chilometriche, N):
        self.ID = int(ID)
        self.direction = direction
        self.km = chilometriche.get(ID)
        self.raw = data[(data['station'] == ID) & (data['direction'] == direction)]
        self.daily = int(self.raw['value'].sum())
        self.getStats(history, chilometriche, N)
        # self.stats = self.getStats(history, chilometriche, N)

    # Calcolo delle statistiche relative alla stazione: media e std.
    # Se le statistiche non sono presenti per questa stazione, prendi le statistiche
    # delle N stazioni vicine.
    def getStats(self, history, chilometriche, N):
        self.lane_selector()
        # -----------------> la condizione dovrebbe essere: se le giornate di dati storici non sono in numero sufficiente: da decidere!!!
        if self.ID not in history['station'].values:
            nearest = self.nearest_stations(chilometriche, history, N)
            history_data = history[(history['station'].isin(nearest)) & (history['lane'].isin(self.lane))]
            history_data = history_data.groupby(['date', 'lane', 'daytype'])['total_traffic'].mean().reset_index()
            print(f'{self.ID:<4} {self.direction:<4} no history, get statistics from {nearest} stations')
        else:
            history_data = history[(history['station'] == self.ID) & (history['lane'].isin(self.lane))]
            print(f'{self.ID:<4} {self.direction:<4}')
        agg_hist = history_data[history_data['lane'].isin(self.lane)].groupby(['date', 'daytype']).agg(
            {'total_traffic': 'sum'}).reset_index()
        self.layer1_stats = agg_hist['total_traffic'].agg(['mean', 'std']).to_dict()

        # Calcolo statistiche distribuzione corsie per layer 2
        layer2_hist = history_data.pivot_table(index='date', columns='lane', values='total_traffic', aggfunc='mean')
        layer2_hist['ratio'] = layer2_hist[self.lane[0]] / layer2_hist[self.lane[1]]
        self.layer2_stats = layer2_hist['ratio'].agg(['mean', 'std']).to_dict()

    # Identifica le N stazioni a valle e le N stazioni a monte più vicine.
    def nearest_stations(self, chilometriche, history, N):
        hist_stations = {k: v for k, v in chilometriche.items() if k in history['station'].unique()}
        diff = {k: abs(v - self.km) for k, v in hist_stations.items()}
        stations_sort = sorted(diff.items(), key=lambda x: x[1])
        nearest = [key for key, _ in stations_sort[:2 * N]]
        return nearest

    # Seleziona il numero delle corsie in base alla direzione di marcia
    def lane_selector(self):
        if self.direction == 'NORD':
            self.lane = ['1', '2']
        elif self.direction == 'SUD':
            self.lane = ['3', '4']
        else:
            self.lane = []

    # Calcola lo z-score per i dati giornalieri.
    def zScore_1(self):
        self.zscore = (self.daily - self.layer1_stats['mean']) / self.layer1_stats['std']

    # Conferma la validazione (layer 1.1) confrontando tra varie stazioni
    def zScore1_1(self, dominio):
        self.zscore1_1 = (self.zscore - dominio.stats1_1['mean']) / dominio.stats1_1['std']

    # Definisci se un set di dati giornalieri è valido o meno in base ai limiti
    # imposti sullo z-score
    def layer1_validation(self, limit):
        if limit.layer1('low') is None and limit.layer1('high') is None:
            self.layer1 = True
        else:
            if limit.layer1('low') is None:
                if self.zscore <= limit.layer1('high'):
                    self.layer1 = True
                else:
                    self.layer1 = False
            elif limit.layer1('high') is None:
                if self.zscore >= limit.layer1('low'):
                    self.layer1 = True
                else:
                    self.layer1 = False
            else:
                if (self.zscore >= limit.layer1('low')) and (self.zscore <= limit.layer1('high')):
                    self.layer1 = True
                else:
                    self.layer1 = False

    def layer1_1_validation(self, limit, dominio):
        if limit.layer1_1('low') is None and limit.layer1_1('high') is None:
            self.layer1_1 = True
        else:
            if limit.layer1_1('low') is None:
                if self.zscore1_1 <= limit.layer1('high'):
                    self.layer1_1 = True
                else:
                    self.layer1 = False
            elif limit.layer1_1('high') is None:
                if self.zscore1_1 >= limit.layer1_1('low'):
                    self.layer1_1 = True
                else:
                    self.layer1_1 = False
            else:
                if (self.zscore1_1 >= limit.layer1_1('low')) and (self.zscore1_1 <= limit.layer1_1('high')):
                    self.layer1_1 = True
                else:
                    self.layer1_1 = False

    def layer3_validation(self):
        df = self.raw.groupby(['time', 'station', 'direction'])['value'].sum().reset_index()
        df['derivata'] = df['value'].pct_change() * 100
        df['is_valid'] = np.where((
                ((df['derivata'] <= -100) & df['value'] > 50) |  # Condizione derivata negativa
                (df['value'].rolling(window=3).sum() == 0)  # Condizione per almeno 3 zeri consecutivi
        ), False, True)
        self.layer3 = df[['time', 'is_valid']].set_index('time')['is_valid'].to_dict()

    def plot(self, layer):
        dir_df = self.raw[self.raw['direction'] == self.direction]
        agg_dir_df = dir_df.groupby('time')['value'].sum().reset_index()
        # agg_dir_df['time'] = pd.to_datetime(agg_dir_df['time'])
        agg_dir_df.plot(x='time', y='value', rot=90, figsize=(10, 6))
        if layer == 'layer3':
            # self.layer3 = {pd.to_datetime(key): value for key, value in self.layer3.items()}
            self.merged = agg_dir_df.merge(pd.DataFrame(list(self.layer3.items()), columns=['time', 'is_valid']),
                                           on='time', how='left')
            plt.scatter(self.merged.index[~self.merged['is_valid']], self.merged['value'][~self.merged['is_valid']],
                        color='red', label='Invalid Values', s=50)
        plt.ylabel('Value')
        plt.grid(True)
        plt.tight_layout()
        plt.legend()
        plt.show()

# DEPRECATED
# def validation(data, params):
#     # ciclo sulle stazioni, calcola z-score
#     out = []
#     for station_code in data.station_list:
#         # inizializza l'oggetto stazione
#         s = Station(data.raw_data, data.history, station_code, data.chilometriche, params.layer1('n'))
#         # calcolo Z-score
#         s.zScore()
#         # assegna flag di validità basato su confronto z-score con valori limite
#         s.validationFlag(params)
#         # lista risultati
#         out.append(s.daily)

#     dfout = pd.concat(out, ignore_index=True)
#     dfout = dfout.sort_values(by=['direction','km'])
#     output = pd.merge(data.raw_data, dfout[['station', 'direction', 'is_valid']], on=['station', 'direction'], how='left')
#     return output
