"""
Created on Tue Aug 16 2022
@author: nicola
"""
import os
import sqlite3
import pandas as pd
import numpy as np


# stima delle emissioni con metodo di copert
def copert_emissions(traffic_df):
    # ------------------------------------------------------------------------------
    # 0. INIZIALIZZAZIONE
    # ------------------------------------------------------------------------------
    # Percorsi dei file di input e output
    input_data_path = f"{os.path.dirname(os.path.abspath(__file__))}/input/"
    input_copert = input_data_path + 'copert55.db'
    # Importa tabella dei coefficienti COPERT da DB
    con = sqlite3.connect(input_copert)
    copert = pd.read_sql_query("SELECT * FROM COPERT", con)
    # Importa file csv di input:
    #   1- fleet-composition: distribuzione percentuale parco macchine per categoria,
    #      alimentazione e classe EURO
    fc = pd.read_csv(input_data_path + 'fc_info.csv')
    #   2- geometria dell'asse stradale (chilometrica e quote)
    geometry = pd.read_csv(input_data_path + 'geometry.csv')
    #   3- lista delle stazioni da non considerare (blacklist)
    blacklist = np.loadtxt(input_data_path + 'blacklist.txt')
    #   4- file della chilometrica (temporaneo fino a quando non sarà esposta in ODH)
    km = pd.read_csv(input_data_path + 'km.csv')
    # ------------------------------------------------------------------------------
    # 1. CALCOLI PRELIMINARI
    # ------------------------------------------------------------------------------
    adt = traffic_df
    # Eliminazione delle stazioni presenti in black list
    adt = adt[~adt.Station.isin(blacklist)]
    # aggiunta valori di chilometrica al df di input (temporaneo fino a quando chilometrica non sarà esposta in ODH)
    adt = pd.merge(adt, km, on='Station')
    # geometria dei tratti di competenza delle stazioni di misura:
    # calcolo della lunghezza dei tratti di competenza delle stazioni di misura e pendenza media.
    station_geometry = RoadGeometry(adt, geometry, copert)
    # Unione dei metadati delle stazioni di misura (RoadSlope, RoadLength) con i dati dei passaggi.
    adt = pd.merge(adt, station_geometry[['Station', 'Lane', 'RoadSlope', 'RoadLength']], on=['Station', 'Lane'])
    # Roadslope è solo per i mezzi pesanti, per gli altri inserisco NaN
    # Questo perché nei coefficienti di COPERT la pendenza della strada non è
    # definita per le altre categorie di veicolo e quindi il successivo merge non
    # può funzionare.
    # Seleziona le categorie per le quali non è definita la RoadSlope in copert
    df = pd.DataFrame(copert, columns=['Category', 'RoadSlope'])
    df = df[df['RoadSlope'].isnull()].drop_duplicates()
    adt['RoadSlope'] = np.where(adt['Category'].isin(df['Category']), float('NaN'), adt['RoadSlope'])
    # Preparazione del dataframe con tutti i dati per il calcolo delle emissioni.
    emission = pd.merge(adt, fc, on=['Category'])
    # Controllo range di validità della velocità per i veicoli:
    # se la velocità misurata è superiore alla massima ammissibile, il calcolo
    # delle emissioni viene svolto con la massima ammissibile. Idem per la minima.
    emission.loc[emission['Speed'] < emission['minSpeed'], 'Speed'] = emission['minSpeed']
    emission.loc[emission['Speed'] > emission['maxSpeed'], 'Speed'] = emission['maxSpeed']
    # Calcolo numero di transiti per ogni tipo di veicolo
    emission['Total_Transits'] = ((emission['Transits'] * emission['PercvsADT']))
    # ------------------------------------------------------------------------------
    # 2. CALCOLO FATTORI DI EMISSIONE, EMISSIONI PER KM, EMISSIONI TOTALI
    # ------------------------------------------------------------------------------
    # Selezione dei coefficienti di COPERT da utilizzare.
    emission = pd.merge(emission, copert, on=['Location', 'Category', 'Fuel', 'ID_Euro', 'RoadSlope'])
    # Fattori di emissione (EF) ed emissioni (E) per ogni categoria.
    emission['EF'] = (emission['Alpha'] * emission['Speed'] * emission['Speed'] + emission['Beta'] * emission['Speed'] + emission['Gamma'] + emission['Delta'] / emission['Speed']) / (emission['Epsilon'] * emission['Speed'] * emission['Speed'] + emission['Zita'] * emission['Speed'] + emission['Hta']) * (1. - emission['EuroReductionFactor']) * (1. - emission['FuelReductionFactor'])
    emission['E'] = emission['EF'] * emission['Total_Transits']
    # Emissioni totali [g/km] alle stazioni di misura.
    emission_agg = emission.groupby(
        ['date', 'time', 'Period', 'Location', 'Station', 'Lane', 'Category', 'km', 'RoadLength', 'Pollutant']).agg(
        {'Total_Transits': sum, 'E': sum}).reset_index()
    # Emissioni totali [g] sui tratti di strada associati alle stazioni.
    # I valori sono arrotondati all'intero, la precisione al grammo è più che
    # sufficiente )
    # emission_agg['total_E_[g]'] = (emission_agg['E'] * emission_agg['RoadLength']).astype(int)
    # Arrotondamento all'intero del numero di transiti
    emission_agg['Total_Transits'] = emission_agg['Total_Transits'].astype(int)
    # ------------------------------------------------------------------------------
    # 3. ESPORTAZIONE RISULTATI
    # ------------------------------------------------------------------------------
    # Seleziona solo le colonne utili e salva in csv i risultati
    return emission_agg[['date', 'time', 'Period', 'Location', 'Station', 'Lane', 'Category', 'km', 'Pollutant', 'Total_Transits', 'E']]


# Definizione dei tratti di competenza per ogni stazione, calcolo di lunghezza e pendenza media per ogni tratto.
def RoadGeometry(data, geom, copert_df):
    # seleziona dai dati in input le chilometriche delle stazioni attive
    dfin = data[['Station', 'Lane', 'km']].drop_duplicates()
    # calcolo dei tratti di competenza delle singole stazioni. Il tratto di
    # competenza serve per estendere l'informazione relativa all'emissione
    # puntuale. Alcune stazioni possono trasmettere i dati solo su alcune
    # corsie. Per questo il calcolo dei tratti di competenza va fatto lungo
    # la singola corsia. Il calcolo restituisce, per ogni stazione e corsia
    # attiva, lunghezza e pendenza media del tratto di competenza.
    output = []
    for lane in dfin.loc[:, 'Lane'].unique():
        station = dfin[dfin['Lane'] == lane]
        # calcolo chilometrica di inizio e fine dei tratti.
        start = []
        end = []
        for i in range(len(station)):
            if i == 0:
                start.append(min(geom['km']))
            else:
                start.append(round((station['km'].iloc[i] + station['km'].iloc[i - 1]) / 2))
                end.append(round((station['km'].iloc[i] + station['km'].iloc[i - 1]) / 2))
        end.append(max(geom['km']))
        station = station.assign(start=start)
        station = station.assign(end=end)
        # calcolo lunghezza dei tratti
        station = station.assign(RoadLength=station['end'] - station['start'])
        # calcolo della quota nei punti di inizio e fine dei tratti
        geom.columns = geom.columns.str.replace('km', 'start')
        station = pd.merge(station, geom, on=['start'])
        geom.columns = geom.columns.str.replace('start', 'end')
        station = pd.merge(station, geom, on=['end'])
        geom.columns = geom.columns.str.replace('end', 'km')
        # calcolo della pendenza media sui singoli tratti
        station['pendenza'] = (station['quota_y'] - station['quota_x']) / (station['RoadLength'] * 1000)
        # dato che il calcolo della pendenza segue la direzione della
        # progressione della chilometrica, la pendenza nelle corsia con
        # direzione opposta va invertita
        station.loc[(station['Lane'] == 1) | (station['Lane'] == 2), 'pendenza'] = -1 * station['pendenza']
        # Arrotondamento delle pendenze ai valori che si trovano nel database
        # di COPERT. Altrimenti, nel merge con i coefficienti di COPERT, i dati
        # relativi ai tratti di strada con pendenza non riconosciuta vengono
        # persi
        RSvalue = pd.Series(copert_df['RoadSlope'].unique()).dropna()
        station['RoadSlope'] = pd.Series(RSvalue.values, RSvalue.values).reindex(station['pendenza'].values, method='nearest').reset_index(drop=True)
        # lista con valori di lunghezza e pendenza calcolati per singola corsia
        output.append(station[['Station', 'Lane', 'RoadLength', 'RoadSlope']])
    # dataframe di output con la geometria di tutti i tratti
    dfout = pd.concat(output)
    dfout.sort_values(by=['Station', 'Lane'], inplace=True)
    return dfout
