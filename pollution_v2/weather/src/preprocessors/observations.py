#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import pandas as pd
import pytz
from astral.sun import sun
from astral import Observer
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom

from common.settings import PARAMETERS_DIR


class Observations:
    """
    Classe per gestire e trasformare i dati delle osservazioni road weather nel file XML observation, input di METRo.

    Attributes:
        - obs_data (pd.DataFrame): df contenente i dati delle osservazioni.
        Deve contenere i seguenti campi: time, prec_qta, stato_meteo, temp_aria,
        temp_rugiada, temp_suolo, vento_vel
        - station_code (str): Codice della stazione roadweather (101, 102, ...).
    """

    def __init__(self, obs_data, station_code):
        self.df = obs_data
        self.station_code = station_code
        self.parameters = ET.parse(f'{PARAMETERS_DIR}/parameters_{station_code}.xml')

    def process(self):
        """
        Processa i dati delle osservazioni
        """
        # Arrotonda il timestamp ai 5 minuti più vicini
        self.df['time'] = pd.to_datetime(self.df['time'])
        self.df.set_index('time', inplace=True)
        self.df = self.df.resample('5min').nearest()
        self.df.reset_index(inplace=True)
        dates_list = self.df['time'].dt.date.unique().tolist()

        # Calcolo presenza di precipitazione
        self.df['pi'] = (self.df['prec_qta'] > 0).astype(int)

        # Stima ora di alba e tramonto
        try:
            root = self.parameters.getroot()
            latitude = float(root.find('.//latitude').text)
            longitude = float(root.find('.//longitude').text)
            sunrise_sunset = sun_times(dates_list, latitude, longitude, 'Europe/Rome')
        except Exception as e:
            # In caso di errore nella lettura dei parametri, usa orari predefiniti
            print(f"Warning: {e}. Using default sunrise and sunset times.")
            sunrise_sunset = []
            for date in dates_list:
                # Combina la data con gli orari 06:00 e 20:00
                sunrise_sunset.append(datetime.combine(date, datetime.min.time().replace(hour=6, minute=0)))
                sunrise_sunset.append(datetime.combine(date, datetime.min.time().replace(hour=20, minute=0)))

        # Calcolo variabili road_condition, conf_level e sst
        for idx, row in self.df.iterrows():
            # Calcolo road_condition e conf_level
            road_condition, conf_level = road_condition_from_observations(
                row['stato_meteo'], row['temp_suolo'], row['temp_rugiada']
            )
            self.df.at[idx, 'sc'] = road_condition
            self.df.at[idx, 'conf_level'] = conf_level

            # Calcolo sst
            if row['time'] in sunrise_sunset:
                self.df.at[idx, 'sst'] = row['temp_suolo']
            else:
                self.df.at[idx, 'sst'] = 9999

            # Se temp_suolo, temp_aria, temp_rugiada e vento_vel sono pari a 0, allora sono NODATA e vanno impostati a 9999
            if row['temp_suolo'] == 0:
                self.df.at[idx, 'temp_suolo'] = 9999
            if row['temp_aria'] == 0:
                self.df.at[idx, 'temp_aria'] = 9999
            if row['temp_rugiada'] == 0:
                self.df.at[idx, 'temp_rugiada'] = 9999
            if row['vento_vel'] == 0:
                self.df.at[idx, 'vento_vel'] = 9999

        # Rinomina i campi del dataframe secondo la dicitura di METRo
        self.df = self.df.rename(columns={'time': 'observation-time',
                                          'temp_suolo': 'st',
                                          'temp_aria': 'at',
                                          'temp_rugiada': 'td',
                                          'vento_vel': 'ws'})

        # definisci un confidence level complessivo da assegnare alla previsione
        if (self.df['conf_level'] == 0).any():
            self.conf_level = 0
        else:
            self.conf_level = 1

        # Filtra e ordina le colonne
        self.df = self.df.filter(items=['observation-time', 'at', 'td', 'pi', 'ws', 'sc', 'st', 'sst'])

    def validate(self):
        """
        Valida i dati delle osservazioni secondo i requisiti richiesti da METRo
        per il file delle osservazioni.

        Raises:
            ValueError: Se i dati non soddisfano un criteri di validità.
        """
        # Controllo 1: Almeno una osservazione deve contenere sia 'sst' che 'st' validi
        valid_sst_st = self.df[(self.df['sst'] != 9999) & (self.df['st'] != 9999)]
        if valid_sst_st.empty:
            raise ValueError("Error: At least one observation must include both a valid 'sst' and 'st' entry.")

        # Controllo 2: L'osservazione contenente sia 'sst' che 'st' deve essere entro 4 ore da un'altra osservazione 'st' valida
        for _, row in valid_sst_st.iterrows():
            observation_time = row['observation-time']
            st_time = self.df[(self.df['st'] != 9999) & (self.df['observation-time'] != observation_time)]
            st_time = st_time[abs(st_time['observation-time'] - observation_time) <= pd.Timedelta(hours=4)]
            if st_time.empty:
                raise ValueError("Error: The observation containing both 'sst' and 'st' must be within 4 hours of another valid 'st' observation.")

        # Controllo 3: Devono esserci almeno due valori 'st' validi
        valid_st = self.df[self.df['st'] != 9999]
        if len(valid_st) < 2:
            raise ValueError("Error: There must be at least two valid 'st' entries.")

        # Controllo 4: Almeno un valore di 'st' deve essere alla prima o alla seconda riga del df
        first_forecast_time = self.df['observation-time'].iloc[0]
        second_forecast_time = self.df['observation-time'].iloc[1] if len(self.df) > 1 else None
        valid_st_first_or_second = self.df[(self.df['st'] != 9999) &
                                            (self.df['observation-time'] == first_forecast_time) |
                                            (self.df['observation-time'] == second_forecast_time)]
        if valid_st_first_or_second.empty:
            raise ValueError("Error: At least one 'st' entry must be at or after the time of the first or second atmospheric forecast.")

    def to_xml(self, filename):
        """
        Converte il DataFrame in un file XML e lo salva nella cartella
        ./observations.

        Raises:
            ValueError: Se il DataFrame non contiene i campi necessari.
        """
        def format_value(value):
            """
            Formatta i valori numerici per l'output XML.

            Args:
                value (float or int): Valore da formattare.

            Returns:
                str: Valore formattato come stringa.
            """
            if value == 9999:
                return '9999'
            elif pd.isna(value):
                return ''
            else:
                return f'{value:.2f}'

        # Verifica la presenza delle colonne richieste
        required_columns = ['observation-time', 'at', 'td', 'st', 'ws', 'pi', 'sc', 'sst']
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"DataFrame is missing the following columns: {', '.join(missing_columns)}")

        # Crea elementi XML
        root = ET.Element('observation')
        header = ET.SubElement(root, 'header')
        ET.SubElement(header, 'filetype').text = 'rwis-observation'
        ET.SubElement(header, 'version').text = '1.0'
        ET.SubElement(header, 'station-id').text = self.station_code
        ET.SubElement(header, 'production-date').text = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        measure_list = ET.SubElement(root, 'measure-list')

        # Aggiungi i dati al file xml
        for _, row in self.df.iterrows():
            measure = ET.SubElement(measure_list, 'measure')
            ET.SubElement(measure, 'observation-time').text = row['observation-time'].strftime('%Y-%m-%dT%H:%M:%SZ')
            ET.SubElement(measure, 'at').text = format_value(row['at'])
            ET.SubElement(measure, 'td').text = format_value(row['td'])
            ET.SubElement(measure, 'st').text = format_value(row['st'])
            ET.SubElement(measure, 'ws').text = format_value(row['ws'])
            ET.SubElement(measure, 'pi').text = str(int(row['pi']))
            ET.SubElement(measure, 'sc').text = str(int(row['sc']))
            ET.SubElement(measure, 'sst').text = format_value(row['sst'])

        # Scrivi su file l'xml formattato
        with open(filename, 'w', encoding='utf-8') as f:
            xml_str = ET.tostring(root, encoding='utf-8', method='xml')
            parsed_xml = minidom.parseString(xml_str)
            parsed_xml = parsed_xml.toprettyxml(indent="  ")
            f.write(parsed_xml)

def road_condition_from_observations(stato_meteo, temp_suolo, temp_rugiada):
    """
    Calcola la condizione della strada e il livello di confidenza della
    previsione di condizione stradale basato sulle osservazioni meteo.

    Args:
        stato_meteo (int): Stato meteo (es pioggia, neve, ...).
        temp_suolo (float): Temperatura del suolo.
        temp_rugiada (float): Temperatura del punto di rugiada.

    Returns:
        tuple: Condizione della strada e livello di confidenza.
    """
    if stato_meteo in (4,5):  # rain/storm
        if temp_suolo > 0:
            road_condition = 2  # wet road
            conf_level = 1
        elif temp_suolo < 0:
            road_condition = 8  # icing road
            conf_level = 1
        else:  # nodata temp_suolo
            road_condition = 2
            conf_level = 0
    elif stato_meteo == 6:  # snow
        if temp_suolo > 0:
            road_condition = 6  # melting snow
            conf_level = 1
        elif temp_suolo < 0:
            road_condition = 3  # ice/snow
            conf_level = 1
        else:  # nodata temp_suolo
            road_condition = 3
            conf_level = 0
    else:  # sun/cloudy
        if temp_suolo == 0 and temp_rugiada == 0:  # nodata temp_suolo and temp_rugiada
            road_condition = 1
            conf_level = 0
        else:
            if temp_suolo < temp_rugiada:
                road_condition = 5  # dew
                conf_level = 1
            else:
                road_condition = 1  # dry road
                conf_level = 1
    return road_condition, conf_level

def sun_times(dates, latitude, longitude, local_timezone='Europe/Rome'):
    """
    Calcola gli orari di alba e tramonto presenti nella serie temporale

    Args:
        dates (list of datetime.date): Liste di date per cui calcolare alba e tramonto.
        latitude (float): Latitudine dell'osservatore (da file parameters).
        longitude (float): Longitudine dell'osservatore (da file parameters).
        local_timezone (str): Fuso orario locale (default: 'Europe/Rome').

    Returns:
        list of datetime.datetime: Lista degli orari di alba e tramonto.
    """
    observer = Observer(latitude=latitude, longitude=longitude)
    local_timezone = pytz.timezone(local_timezone)

    def round_datetime_to_nearest_five_minutes(dt):
        minutes = (dt.minute // 5) * 5
        remainder = dt.minute % 5
        if remainder >= 2.5:
            minutes += 5
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)

    results = []
    for date in dates:
        s = sun(observer, date=date, tzinfo=local_timezone)
        sunrise_rounded = round_datetime_to_nearest_five_minutes(s['sunrise'].astimezone(local_timezone))
        sunset_rounded = round_datetime_to_nearest_five_minutes(s['sunset'].astimezone(local_timezone))
        results.append(sunrise_rounded.replace(tzinfo=None))
        results.append(sunset_rounded.replace(tzinfo=None))

    return results
