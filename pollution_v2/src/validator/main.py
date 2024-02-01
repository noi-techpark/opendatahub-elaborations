# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from validator.Moduli import Parametri, Dominio, Station
from validator.dataConnector import Input

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
params = Parametri('../../config/validator.yaml')
db = params.parametri['db_path']
day = params.parametri['day']
plot = params.parametri['plot']
# -----------------------------------------------------------------------------
# Inizializzazione stazioni
# -----------------------------------------------------------------------------
print(f'...initializing data for day {day}')
data = Input(day, db)
A22 = Dominio()
for index, row in data.station_list.iterrows():
    stationID = row['station']
    direction = row['direction']
    # inizializza l'oggetto stazione
    s = Station(data.raw_data, data.history, stationID, direction, data.chilometriche, params.layer1('n'))
    A22.add_station(s)
print('...validation starting')

# -----------------------------------------------------------------------------
# Layer 1
# -----------------------------------------------------------------------------
for s in A22.station_list:
    # calcolo Z-score
    s.zScore_1()
    # assegna flag di validità basato su confronto z-score con valori limite
    s.layer1_validation(params)
    if s.layer1 == False:
        print(f'{s.ID:<4} {s.direction:<4} not valid for layer 1')
        if plot:
            s.plot('layer1')
        A22.layer1_not_valid_station(s)
# -----------------------------------------------------------------------------
# Layer 1.1 - update validation flag dopo confronto con altre stazioni
# -----------------------------------------------------------------------------
A22.zscore_statistics()
for s in A22.station_list:
    s.zScore1_1(A22)
    s.layer1_1_validation(params, A22)
    if s.layer1_1 == False:
        if s in A22.layer1_not_valid:
            print(f'{s.ID:<4} {s.direction:<4} not valid for layer 1.1 (confirmed)')
        else:
            print(f'{s.ID:<4} {s.direction:<4} not valid for layer 1.1')
        A22.layer1_1_not_valid_station(s)
# -----------------------------------------------------------------------------
# Layer 2
# -----------------------------------------------------------------------------
# da concludere...
# -----------------------------------------------------------------------------
# Layer 3
# -----------------------------------------------------------------------------
for s in A22.station_list:
    s.layer3_validation()
    if any(not value for value in s.layer3.values()):
        print(f'{s.ID:<4} {s.direction:<4} not valid for layer 3')
        if plot:
            s.plot('layer3')
        A22.layer3_not_valid_station(s)
print('...validation complete!')
# -----------------------------------------------------------------------------
# Output - struttura dati da concordare...
# -----------------------------------------------------------------------------
