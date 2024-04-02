# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

class Dominio:
    def __init__(self, input_data):
        self.input = input_data
        self.station_list = []
        self.layer1_not_valid = []
        self.layer1_1_not_valid = []
        self.layer2_not_valid = []
        self.layer3_not_valid = []
        self.stats1_1 = {}

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
        for direction in ['SUD', 'NORD']:
            daily_list = [stazione.daily for stazione in self.station_list if stazione.direction == direction]
            daily_array = np.array([val if val is not None else np.nan for val in daily_list])
            self.stats1_1[direction] = {'mean': np.nanmean(daily_array), 'std': np.nanstd(daily_array)}

    def is_valid(self, row):
        return True if (row['layer_1'] is True) and (row['layer_3'] is True) else False

    def overall_validation(self):
        output = pd.DataFrame()

        for s in self.station_list:
            df = s.raw[['time', 'station_code', 'variable', 'value']]
            if s.layer1 is None:
                df['layer_1'] = 999
            else:
                df['layer_1'] = s.layer1

            if s.layer1_1 is None:
                df['layer_1_1'] = 999
            else:
                df['layer_1_1'] = s.layer1_1

            if s.layer2 is None:
                df['layer_2'] = 999
            else:
                df['layer_2'] = s.layer2

            layer3 = pd.DataFrame(list(s.layer3.items()), columns=['time', 'layer_3'])
            layer3['layer_3'] = layer3['layer_3'].astype(int)
            df = pd.merge(df, layer3, on='time', how='left')
            output = pd.concat([output, df], ignore_index=True)

        for index, row in output.iterrows():
            if row['layer_1'] == 1:
                is_valid = 1
            elif row['layer_1'] == 0:
                if row['layer_1_1'] == 1:
                    is_valid = 1
                else:
                    is_valid = 0
            else:
                is_valid = 999

            if is_valid == 1 or is_valid == 999:
                if row['layer_3'] == 1:
                    is_valid = 1
                elif row['layer_3'] == 0:
                    is_valid = 0

            output.at[index, 'is_valid'] = is_valid

        self.output = output[['time', 'station_code', 'variable', 'value', 'is_valid']]
