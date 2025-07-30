#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

class Forecast:
    def __init__(self, station_code):
        self.station_code = station_code

    def download_xml(self, forecast_url_xml):
        """
        Scarica i dati delle previsioni meteorologiche dall'endpoint CISMA.
        Args: forecast_url_xml (str): URL del file XML delle previsioni da scaricare.
        """
        url_xml = forecast_url_xml
        with urllib.request.urlopen(url_xml) as response:
            xml_data = response.read()
            self.load_xml(xml_data)

    def load_xml(self, xml_data):
        """
        Carica i dati delle previsioni meteorologiche dall'XML.
        Args: xml_data (str): contenuto del file XML delle previsioni da scaricare.
        """
        self.tree = ET.ElementTree(ET.fromstring(xml_data))
        self.root = self.tree.getroot()
        # estrai il datetime corrispondente iniziale (per definire sovrapposizione con observations)
        first_forecast_time = self.root.find(".//forecast-time").text
        self.start = datetime.strptime(first_forecast_time, "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%dT%H:%M')

    def interpolate_data(self, point1, point2, timestamp):
        """
        Interpola i dati meteorologici.
        Args:
            point1 (Element): Il primo punto di previsione XML.
            point2 (Element): Il secondo punto di previsione XML.
            timestamp (datetime): Il timestamp per cui interpolare i dati.
        Returns:
            Element: Un nuovo elemento XML con i dati interpolati.
        """
        time1 = datetime.strptime(point1.find('forecast-time').text, "%Y-%m-%dT%H:%M:%SZ")
        time2 = datetime.strptime(point2.find('forecast-time').text, "%Y-%m-%dT%H:%M:%SZ")

        delta_time = time2 - time1
        fraction = (timestamp - time1).total_seconds() / delta_time.total_seconds()

        interpolated_data = ET.Element("prediction")
        interpolated_data.text = point1.text
        interpolated_data.tail = point1.tail

        interpolated_time = time1 + fraction * delta_time
        interpolated_time_element = ET.SubElement(interpolated_data, 'forecast-time')
        interpolated_time_element.text = interpolated_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        interpolated_time_element.tail = point1.find('forecast-time').tail

        for element in point1:
            if element.tag != 'forecast-time':
                new_element = ET.SubElement(interpolated_data, element.tag)

                value1 = float(point1.find(element.tag).text)
                value2 = float(point2.find(element.tag).text)
                interpolated_value = value1 + fraction * (value2 - value1)

                if element.tag == 'cc':
                    interpolated_value = round(interpolated_value)
                else:
                    interpolated_value = round(interpolated_value, 1)

                new_element.text = str(interpolated_value)
                new_element.tail = element.tail

        interpolated_data.tail = point1.tail
        return interpolated_data

    def interpolate_hourly(self):
        """
        Interpola le previsioni meteorologiche orarie tra i punti di previsione esistenti.
        Inserisce le nuove previsioni interpolate nella lista esistente, ordinandole in base al tempo.
        """
        predictions = self.root.find(".//prediction-list")
        new_interpolated_predictions = []

        for i in range(len(predictions) - 1):
            point1 = predictions[i]
            point2 = predictions[i + 1]

            time1 = datetime.strptime(point1.find('forecast-time').text, "%Y-%m-%dT%H:%M:%SZ")
            time2 = datetime.strptime(point2.find('forecast-time').text, "%Y-%m-%dT%H:%M:%SZ")

            if (time2 - time1).total_seconds() > 3600:
                num_interpolations = int((time2 - time1).total_seconds() / 3600) - 1
                for j in range(num_interpolations):
                    timestamp = time1 + timedelta(hours=j + 1)
                    new_interpolated_prediction = self.interpolate_data(point1, point2, timestamp)
                    new_interpolated_predictions.append(new_interpolated_prediction)

        for new_interpolated_prediction in new_interpolated_predictions:
            forecast_time_str = new_interpolated_prediction.find('forecast-time').text
            forecast_time = datetime.strptime(forecast_time_str, '%Y-%m-%dT%H:%M:%SZ')

            insertion_index = 0
            for existing_prediction in predictions:
                existing_forecast_time_str = existing_prediction.find('forecast-time').text
                existing_forecast_time = datetime.strptime(existing_forecast_time_str, '%Y-%m-%dT%H:%M:%SZ')

                if forecast_time < existing_forecast_time:
                    break
                insertion_index += 1

            predictions.insert(insertion_index, new_interpolated_prediction)

    def negative_radiation_filter(self):
        """
        Filtra i valori di radiazione negativa impostandoli a zero.
        """
        tags_to_check = ['ir', 'sf']
        predictions = self.root.find(".//prediction-list")

        for prediction in predictions:
            for tag in tags_to_check:
                tag_element = prediction.find(tag)
                if tag_element is not None:
                    value = float(tag_element.text)
                    if value < 0:
                        tag_element.text = '0.0'

    def get_forecast_datetime(self):
        header = self.root.find("header")
        production_date_element = header.find("production-date")
        forecast_date = production_date_element.text
        return forecast_date

    def to_xml(self, filename):
        self.tree.write(filename, encoding="utf-8", xml_declaration=True)
