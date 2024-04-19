# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Il metodo utilizzato per validare i dati per il giorno specificato
def validator(day, raw_data, history, km, station_type, config = '../../config/validator.yaml'):
    """
    :param day: data per la quale validare i dati
    :param raw_data: dataframe con i dati grezzi
    :param history: dataframe con i dati storici
    :param km: dataframe con i dati chilometrici
    :param station_type: dataframe con tipo stazione
    :param config: percorso file di configurazione
    """

    # -------------------------------------------------------------------------
    # Import Moduli
    # -------------------------------------------------------------------------
    from Parametri import Parametri
    from Input import Input
    from Dominio import Dominio
    from Station import Station
    import pandas as pd
    pd.options.mode.chained_assignment = None

    # -------------------------------------------------------------------------
    # Configurazione parametri
    # -------------------------------------------------------------------------
    params = Parametri(config)
    plot = params.parametri['plot']

    # -------------------------------------------------------------------------
    # Dati input
    # -------------------------------------------------------------------------
    data = Input(day, raw_data, history, km, station_type)

    # -------------------------------------------------------------------------
    # Inizializzazione dominio e stazioni
    # -------------------------------------------------------------------------
    print(f'...initializing data for day {day}')
    A22 = Dominio(data)
    for index, row in data.station_list.iterrows():
        if data.station_type[row['station']] != 'TVCC' or data.station_type[row['station']] != 'RADAR':
            # inizializza l'oggetto stazione e aggiungilo all'oggetto dominio
            s = Station(data.raw_data, data.history, row['station'], row['direction'], data.chilometriche, params.layer1('n'))
            A22.add_station(s)
    print('-----------------------')
    # -------------------------------------------------------------------------
    # Layer 1
    # -------------------------------------------------------------------------
    print('...validation starting')
    for s in A22.station_list:
        if s.skip_validation == False:
            # calcolo Z-score
            s.zScore_1()
            # assegna flag di validità basato su confronto z-score con valori limite
            s.layer1_validation(params)
            if s.layer1 == False:
                A22.layer1_not_valid_station(s)
                print(f'{s.ID:<4} {s.direction:<4} not valid for layer 1')
                if plot:
                    s.plot('layer1')
    # -------------------------------------------------------------------------
    # Layer 1.1
    # -------------------------------------------------------------------------
    A22.zscore_statistics()
    for s in A22.station_list:
        if s.skip_validation == False:
            s.zScore1_1(data.chilometriche, A22, params.layer1_1('n'))
            s.layer1_1_validation(params, A22)
            if s.layer1_1 == False:
                if s in A22.layer1_not_valid:
                    print(f'{s.ID:<4} {s.direction:<4} not valid for layer 1.1 (confirmed)')
                else:
                    print(f'{s.ID:<4} {s.direction:<4} not valid for layer 1.1')
                A22.layer1_1_not_valid_station(s)
                if plot:
                    s.plot('layer1')
            else:
                if s in A22.layer1_not_valid:
                    print(f'{s.ID:<4} {s.direction:<4} valid for layer 1.1 (not confirmed)')
    # -------------------------------------------------------------------------
    # Layer 2
    # -------------------------------------------------------------------------
    for s in A22.station_list:
        if s.skip_validation == False and s.skip_l2_validation == False:
            # calcolo Z-score
            s.zScore_2()
            # assegna flag di validità basato su confronto z-score con valori limite
            s.layer2_validation(params, A22)
            if s.layer2 == False:
                print(f'{s.ID:<4} {s.direction:<4} not valid for layer 2')
                A22.layer2_not_valid_station(s)
    # -------------------------------------------------------------------------
    # Layer 3
    # -------------------------------------------------------------------------
    for s in A22.station_list:
        s.layer3_validation()
        if any(not value for value in s.layer3.values()):
            print(f'{s.ID:<4} {s.direction:<4} not valid for layer 3')
            if plot:
                s.plot('layer3')
            A22.layer3_not_valid_station(s)
    print('-----------------------')
    print('...validation complete!')
    # -----------------------------------------------------------------------------
    # Output
    # -----------------------------------------------------------------------------
    # dataframe output [time, station_code, variable, value, is_valid]
    A22.overall_validation()
    dfout = A22.output

    return dfout
