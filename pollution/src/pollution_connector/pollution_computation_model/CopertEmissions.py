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
    # aggiunta valori di chilometrica al df di input se non è presente
    adt = pd.merge(adt, km, on='Station', how='left')
    # trasformazione valore chilometrica da metri a chilometri
    adt['KM'] = adt['KM'].astype(float).div(1000)
    # se non è presente il valore di chilometrica, allora prendilo da file 'km.csv'
    # se km == nan, allora pendenza = 0
    adt['KM'] = adt['KM'].fillna(adt['km'])
    adt.drop('km', axis=1, inplace=True)
    adt.rename(columns={'KM': 'km'}, inplace=True)
    adt['KM'] = adt['km'].astype(float).round()
    # assegnazione valore di pendenza ad ogni stazione, basato su chilometrica più vicina
    if ('RoadSlope' in copert) and ('RoadSlope' in geometry):
        adt = pd.merge(adt, geometry[['KM', 'RoadSlope']], on='KM')
        adt.loc[(adt['Lane'] == 1) | (adt['Lane'] == 2), 'RoadSlope'] = -1 * adt['RoadSlope']
        # Roadslope è solo per i mezzi pesanti, per gli altri inserisco NaN.
        # Seleziona le categorie per le quali non è definita la RoadSlope in copert
        df = pd.DataFrame(copert, columns=['Category', 'RoadSlope'])
        df = df[df['RoadSlope'].isnull()].drop_duplicates()
        adt['RoadSlope'] = np.where(adt['Category'].isin(df['Category']), float('NaN'), adt['RoadSlope'])
    # Preparazione del dataframe con tutti i dati per il calcolo delle emissioni.
    emission = pd.merge(adt, fc, on=['Category'])
    # Calcolo numero di transiti per ogni tipo di veicolo
    emission['Total_Transits'] = ((emission['Transits'] * emission['PercvsADT']))
    # ------------------------------------------------------------------------------
    # 2. CALCOLO FATTORI DI EMISSIONE, EMISSIONI PER KM, EMISSIONI TOTALI
    # ------------------------------------------------------------------------------
    # Selezione dei coefficienti di COPERT da utilizzare
    if ('RoadSlope' in copert) and ('RoadSlope' in geometry):
        emission = pd.merge(emission, copert, on=['Location', 'Category', 'Fuel', 'ID_Euro', 'RoadSlope'])
    elif ('RoadSlope' in copert) and ('RoadSlope' not in geometry):
        copert = copert[(copert['RoadSlope'] == 0) | (copert['RoadSlope'].isnull())]
        emission = pd.merge(emission, copert, on=['Location', 'Category', 'Fuel', 'ID_Euro', 'RoadSlope'])
    else:
        emission = pd.merge(emission, copert, on=['Location', 'Category', 'Fuel', 'ID_Euro'])
    # Controllo range di validità della velocità per i veicoli:
    # se la velocità misurata è superiore alla massima ammissibile, il calcolo
    # delle emissioni viene svolto con la massima ammissibile. Idem per la minima.
    emission.loc[emission['Speed'] < emission['MinSpeed'], 'Speed'] = emission['MinSpeed']
    emission.loc[emission['Speed'] > emission['MaxSpeed'], 'Speed'] = emission['MaxSpeed']
    # Fattori di emissione (EF) ed emissioni (E) per ogni categoria.
    emission['EF'] = (emission['Alpha'] * emission['Speed'] * emission['Speed'] + emission['Beta'] * emission['Speed'] + emission['Gamma'] + emission['Delta'] / emission['Speed']) / (emission['Epsilon'] * emission['Speed'] * emission['Speed'] + emission['Zita'] * emission['Speed'] + emission['Hta']) * (1. - emission['EuroReductionFactor']) * (1. - emission['FuelReductionFactor'])
    emission['E'] = emission['EF'] * emission['Total_Transits']
    # Emissioni totali [g/km] alle stazioni di misura.
    emission_agg = emission.groupby(
        ['date', 'time', 'Period', 'Location', 'Station', 'Lane', 'Category', 'km', 'Pollutant']).agg(
        {'Total_Transits': sum, 'E': sum}).reset_index()
    # Emissioni totali [g] sui tratti di strada associati alle stazioni.
    # I valori sono arrotondati all'intero, la precisione al grammo è più che
    # sufficiente)
    # Arrotondamento all'intero del numero di transiti
    emission_agg['Total_Transits'] = emission_agg['Total_Transits'].round().astype(int)
    # ------------------------------------------------------------------------------
    # 3. ESPORTAZIONE RISULTATI
    # ------------------------------------------------------------------------------
    # Ritorna solo le colonne utili
    return emission_agg[['date', 'time', 'Period', 'Location', 'Station', 'Lane', 'Category', 'km', 'Pollutant', 'Total_Transits', 'E']]
