# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

logger = logging.getLogger("pollution_v2.validator.Station")

class Station:
    # Inizializza l'oggetto stazione con le caratteristiche identificative
    # e i dati giornalieri.
    def __init__(self, data, history, ID, direction, chilometriche, N):
        self.ID = int(ID)
        self.direction = direction
        self.km = chilometriche.get(ID)
        self.raw = data[(data['station'] == ID) & (data['direction'] == direction)]
        self.daily = int(self.raw['value'].sum())
        self.skip_validation = False
        self.getStats(history, chilometriche, N)
        self.zscore1 = 0
        self.zscore1_1 = 0
        self.zscore2 = 0

    # Calcolo delle statistiche relative alla stazione: media e std.
    # Se le statistiche non sono presenti per questa stazione, prendi le statistiche
    # delle N stazioni vicine.
    def getStats(self, history, chilometriche, N):
        self.lane_selector()
        history_len = history[history['station'] == self.ID].shape[0]
        if self.ID not in history['station'].values or history_len < 10:
            if self.ID not in chilometriche.index.values:
                logger.info(f'{self.ID:<4} {self.direction:<4} no history, no information about position --> skip layer 1, 1.1, 2')
                self.skip_validation = True
                self.layer1 = None
                self.layer1_1 = None
                self.layer2 = None
                self.layer3 = None
                return None
            else:
                nearest = self.nearest_stations_L1(chilometriche, history, N)
                history_data = history[(history['station'].isin(nearest)) & (history['lane'].isin(self.lane))]
                history_data = history_data.groupby(['date', 'lane', 'daytype'])['total_traffic'].mean().reset_index()
                logger.info(f'{self.ID:<4} {self.direction:<4} no history, get statistics from {nearest} stations')
        else:
            history_data = history[(history['station'] == self.ID) & (history['lane'].isin(self.lane))]
            logger.debug(f'{self.ID:<4} {self.direction:<4}')
        if history_data is not None:
            agg_hist = history_data[history_data['lane'].isin(self.lane)].groupby(['date', 'daytype']).agg({'total_traffic': 'sum'}).reset_index()
        else:
            self.skip_validation = True
        # TODO move in previous if?
        self.layer1_stats = agg_hist['total_traffic'].agg(['mean', 'std']).to_dict()

        # Calcolo statistiche distribuzione corsie per layer 2
        layer2_hist = history_data.pivot_table(index='date', columns='lane', values='total_traffic', aggfunc='mean')
        if layer2_hist.shape[1] == 2:
            layer2_hist['ratio'] = layer2_hist[self.lane[0]] / layer2_hist[self.lane[1]]
            self.layer2_stats = layer2_hist['ratio'].agg(['mean', 'std']).to_dict()
        else:
            logger.info(f'{self.ID:<4} {self.direction:<4} no lane history --> skip layer 2 validation')

    # Identifica le N stazioni a valle e le N stazioni a monte più vicine.
    def nearest_stations_L1(self, chilometriche, history, N):
        hist_stations = {k: v for k, v in chilometriche.items() if k in history['station'].unique()}
        diff = {k: abs(v - self.km) for k, v in hist_stations.items()}
        stations_sort = sorted(diff.items(), key=lambda x: x[1])
        nearest = [key for key, _ in stations_sort[:2*N]]
        return nearest

    def nearest_stations_L1_1(self, chilometriche, dominio, N):
        station_list = [stazione.ID for stazione in dominio.station_list if stazione.direction == self.direction]
        stations = {k: v for k, v in chilometriche.items() if k in station_list}
        diff = {k: abs(v - self.km) for k, v in stations.items()}
        stations_sort = sorted(diff.items(), key=lambda x: x[1])
        nearest = [key for key, _ in stations_sort[:2*N]]
        nearest.remove(self.ID)
        return nearest

    # Seleziona il numero delle corsie in base alla direzione di marcia
    def lane_selector(self):
        if self.direction == 'NORD':
            self.lane = ['1','2']
        elif self.direction == 'SUD':
            self.lane = ['3','4']
        else:
            self.lane = []

    # Calcola lo z-score per i dati giornalieri.
    def zScore_1(self):
        try:
            self.zscore1 = (self.daily - self.layer1_stats['mean'])/self.layer1_stats['std']
        except Exception as e:
            logger.warning(f'error computing zscore layer 1 for {self.ID} {self.direction}: {e}')
            self.zscore1 = None

    def zScore1_1(self, chilometriche, dominio, N):
        try:
            nearest = self.nearest_stations_L1_1(chilometriche, dominio, N)
            nearest_data = [stazione.daily for stazione in dominio.station_list if stazione.ID in nearest and stazione.direction == self.direction]
            self.layer1_1_stats = {'mean': np.mean(nearest_data), 'std': np.std(nearest_data)}
            self.zscore1_1 = (self.daily - np.mean(nearest_data))/np.std(nearest_data)
        except Exception as e:
            logger.warning(f'error computing zscore layer 1.1 for {self.ID} {self.direction}: {e}')
            self.zscore1_1 = None

    # Calcola lo z-score per i dati giornalieri sulla base della corsia.
    def zScore_2(self):
        traffic_per_lane = self.raw.groupby(['lane'])['value'].sum().reset_index().sort_values(by='lane')
        if len(traffic_per_lane) == 2:
            if traffic_per_lane.iloc[1]['value'] != 0:
                try:
                    lane_ratio = traffic_per_lane.iloc[0]['value']/traffic_per_lane.iloc[1]['value']
                    self.zscore2 = (lane_ratio - self.layer2_stats['mean'])/self.layer2_stats['std']
                except KeyError as e:
                    logger.warning(f'error computing zscore layer 2 for {self.ID} {self.direction}: {e}')
                    self.zscore2 = None
                except Exception as e:
                    # TODO is there a way to manage better this case?
                    logger.warning(f'Exception computing zscore layer 2 for {self.ID} {self.direction}: {e}')
                    self.zscore2 = None
            else:
                self.zscore2 = None
        else:
            self.zscore2 = None

    # Definisci se un set di dati giornalieri è valido o meno in base ai limiti
    # imposti sullo z-score
    def layer1_validation(self, limit):
        if self.zscore1 is not None:
            if limit.layer1('low') is None and limit.layer1('high') is None:
                self.layer1 = True
            else:
                if limit.layer1('low') is None:
                    if self.zscore1 <= limit.layer1('high'):
                        self.layer1 = True
                    else:
                        self.layer1 = False
                elif limit.layer1('high') is None:
                    if self.zscore1 >= limit.layer1('low'):
                        self.layer1 = True
                    else:
                        self.layer1 = False
                else:
                    if (self.zscore1 >= limit.layer1('low')) and (self.zscore1 <= limit.layer1('high')):
                        self.layer1 = True
                    else:
                        self.layer1 = False
        else:
           self.layer1 = None

    def layer1_1_validation(self, limit, dominio):
        if self.zscore1_1 is not None:
            if limit.layer1_1('low') is None and limit.layer1_1('high') is None:
                self.layer1_1 = True
            else:
                if limit.layer1_1('low') is None:
                    if self.zscore1_1 <= limit.layer1_1('high'):
                        self.layer1_1 = True
                    else:
                        self.layer1_1 = False
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
        else:
           self.layer1_1 = None

    def layer2_validation(self, limit, dominio):
        if self.zscore2 is not None:
            if limit.layer2('low') is None and limit.layer2('high') is None:
                self.layer2 = True
            else:
                if limit.layer2('low') is None:
                    if self.zscore2 <= limit.layer2('high'):
                        self.layer2 = True
                    else:
                        self.layer2 = False
                elif limit.layer2('high') is None:
                    if self.zscore2 >= limit.layer2('low'):
                        self.layer2 = True
                    else:
                        self.layer2 = False
                else:
                    if (self.zscore2 >= limit.layer2('low')) and (self.zscore2 <= limit.layer2('high')):
                        self.layer2 = True
                    else:
                        self.layer2 = False
        else:
           self.layer2 = None

    def layer3_validation(self):
        df = self.raw.groupby(['time', 'station', 'direction'])['value'].sum().reset_index()
        df['derivata'] = df['value'].pct_change() * 100
        df['deriv'] = np.where((df['derivata'] <= -99), False, True)
        df['shift'] = np.where((df['value'].shift(1) >= 50), False, True)
        df['is_valid'] = np.where(
            ((df['derivata'] <= -99) & (df['value'].shift(1) >= 50 ))|
            (df['value'].rolling(window=4).sum() == 0) |
            (df['value'].rolling(window=4).sum().shift(-3) == 0) |
            (df['value'].rolling(window=4).sum().shift(-2) == 0) |
            (df['value'].rolling(window=4).sum().shift(-1) == 0),
            False, True
        )
        self.layer3 = df[['time', 'is_valid']].set_index('time')['is_valid'].to_dict()

    def plot(self, layer):
        dir_df = self.raw[self.raw['direction'] == self.direction]
        agg_dir_df = dir_df.groupby('time')['value'].sum().reset_index()
        agg_dir_df.plot(x='time', y='value', rot=90, figsize=(10, 6))
        if layer == 'layer3':
            self.merged = agg_dir_df.merge(pd.DataFrame(list(self.layer3.items()), columns=['time', 'is_valid']), on='time', how='left')
            plt.scatter(self.merged.index[~self.merged['is_valid']], self.merged['value'][~self.merged['is_valid']], color='red', label='Invalid values', s=50)
        plt.ylabel('Vehicles/10min')
        plt.grid(True)
        plt.tight_layout()
        plt.legend()
        plt.title(str(self.ID) + ' ' + str(self.direction))
        plt.show()
