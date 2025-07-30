#!/usr/bin/python

# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from io import StringIO

import pandas as pd
import numpy as np
import datetime
import math
import sys
import csv
import os

def MeteoFromODH(enabled_domains, start_datetime, end_datetime, csv_content: str = None):

    """
    TODO U-HOPPER: Implement this function to fetch meteorological data from ODH.
    La funzione deve restituire un dataframe con la stessa struttura e campi del csv di esempio './data/input/meteo/df_meteo_example.csv'
    contenente tutti i dati meteo di tutti i domini abilitati alla simulazione.
    'enabled_domains' è la lista contenente tutte le informazioni di config.yaml per i domini abilitati da cui ricavare tipo e id della sorgente dati.
    start_datetime (definito come argomento al main.py) e end_datetime (start_datetime + 1h) definiscono l'intervallo temporale da considerare, sono nel formato YYYY-mm-dd HH:MM:SS
    """

    if csv_content:
        csv = StringIO(csv_content)
    else:
        # Questo è solo un dataset di esempio per far girare il codice
        csv = StringIO('../data/input/meteo/df_meteo_example.csv')

    df = pd.read_csv(csv)
    return df

def mean_wind_direction(directions):
    """
    Calculate the average wind direction.

    """
    # Remove NaN values
    directions = directions[~np.isnan(directions)]
    # Calculate the Cartesian components
    directions_rad = np.radians(directions)
    x = np.cos(directions_rad)
    y = np.sin(directions_rad)
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    # Calculate the average direction
    mean_angle_rad = np.arctan2(mean_y, mean_x)
    mean_angle_deg = np.degrees(mean_angle_rad)
    # Ensure the result is between 0° and 360°
    if mean_angle_deg < 0:
        mean_angle_deg += 360

    return mean_angle_deg

def PG_stability(rad, ws, date):
    # if day
    if rad > 0:
        if ws <= 2:
            if rad >= 540:
                CLASS = 'A'
            elif rad < 540 and rad >= 270:
                CLASS = 'B'
            elif rad < 270 and rad >= 140:
                CLASS = 'C'
            else:
                CLASS = 'D'
        elif ws >= 2 and ws < 3:
            if rad >= 700:
                CLASS = 'A'
            elif rad < 700 and rad >= 270:
                CLASS = 'B'
            elif rad < 270 and rad >= 140:
                CLASS = 'C'
            else:
                CLASS = 'D'
        elif ws >= 3 and ws < 4:
            if rad >= 400:
                CLASS = 'B'
            elif rad < 400 and rad >= 140:
                CLASS = 'C'
            else:
                CLASS = 'D'
        elif ws >= 4 and ws < 5:
            if rad >= 540:
                CLASS = 'B'
            elif rad < 540 and rad >= 270:
                CLASS = 'C'
            else:
                CLASS = 'D'
        elif ws >= 5 and ws < 6:
            if rad >= 270:
                CLASS = 'C'
            else:
                CLASS = 'D'
        else:
            if rad >= 540:
                CLASS = 'C'
            else:
                CLASS = 'D'
    # if night
    else:
        # if summer
        if date.month in [6,7,8]:
            CLASS = 'D'
        # if winter
        elif date.month in [12,1,2]:
            if ws <= 3:
                CLASS = 'F'
            elif ws > 3 and ws <= 5:
                CLASS = 'E'
            else:
                CLASS = 'D'
        # if spring/autumn
        else:
            if ws <= 2:
                CLASS = 'F'
            elif ws > 2 and ws <= 3:
                CLASS = 'E'
            else:
                CLASS = 'D'
    return CLASS

def MixingHeight(stability, default=-99):
    zic = {
        "A" : 1300,
        "B" : 900,
        "C" : 850,
        "D" : 800,
        "E" : 400,
        "F" : 100
        }
    return zic.get(stability, default)

def MoninObukhov(stability, default=-99):
    MOL = {
        "A" : -2,
        "B" : -10,
        "C" : -100,
        "D" : 1000,
        "E" : 100,
        "F" : 200
        }
    return MOL.get(stability, default)

def NetRadiation(rad, date):
    if rad > 0:
        netrad = rad/2
    else:
        if date.month in [6,7,8]:
            netrad = -20
        elif date.month in [12,1,2]:
            netrad = -40
        else:
            netrad = -30
    return netrad

def SensHeat(netrad, B0):
    Hsens = 0.9*netrad/(1+1/B0)
    return Hsens

def meteo2sfc(df, output_sfc):
    lat = "46.5000N"
    lon = "11.3000E"
    ua_id = "77777"
    sf_id = "88888"
    os_id = "99999"
    version = "6341"
    # von Kármán constant
    k = 0.4
    # gravity acceleration [m s-2]
    g = 9.81
    # specific heat at constant pressure [J kg-1 K-1]
    cp = 1004
    # air density
    rho = 1.29
    # Bowen Ratio
    B0 = 0.8
    # vertical potential temperature gradient above PBL
    vptg = 99
    # surface roughness
    z0 = 0.1
    # albedo
    r = -9
    # reference height for wind measurement [m]
    zref = 10
    # reference height for temperature measurement [m]
    ztemp = 2
    ipcode = 99
    pamt = 99
    # relative humidity
    rh = -99
    pres = 99
    ccvr = 99

    if os.path.exists(output_sfc):
        os.remove(output_sfc)
    # read time variables
    df = df.copy()
    df.loc[:, 'timestamp'] = pd.to_datetime(df['timestamp'])
    timestamp = df['timestamp'].min()
    date = timestamp.date()
    year = timestamp.strftime('%y')
    month = timestamp.strftime('%m')
    day = timestamp.strftime('%d')
    j_day = timestamp.strftime('%j')
    hour = timestamp.strftime('%H')
    # read measured variables
    radglob = round(df['global-radiation'].mean(), 1)
    ws = round(df['wind-speed'].mean(), 1)
    wd = round(mean_wind_direction(df['wind-direction'].values), 2)
    temp = round(df['air-temperature'].mean(), 2) + 273.15
    rh = round(df['air-humidity'].mean(), 1)
    # calculate derived variables
    if radglob != None:
        stability_class = PG_stability(radglob, ws, date)
        MOL = round(MoninObukhov(stability_class), 1)
        nrad = round(NetRadiation(radglob, date), 1)
    else:
        if hour >= 21 or hour < 5:
            MOL = 25
            stability_class = 'E'
            nrad = 0
        elif hour >= 9 and hour < 17:
            MOL = -10
            stability_class = 'B'
            nrad = 200
        else:
            MOL = 200
            stability_class = 'F'
            nrad = 50

    H = round(SensHeat(nrad, B0), 1)
    ustar = round(pow(abs(-(k*g*H*MOL)/(cp*rho*temp)), 1/3), 3)
    zic = round(MixingHeight(stability_class), 0)
    zim = round(max(50, 2400 * pow(ustar, 1.5)), 0)
    if H >= 0:
        wstar = round(pow((g*H*zic)/(cp*rho*temp), 1/3) if zic > 0 else 0, 3)
    else:
        wstar = round(-pow(abs((g*H*zic)/(cp*rho*temp)), 1/3) if zic > 0 else 0, 3)
    # write sfc file
    output = open(output_sfc, "at")
    output.write("   %s    %s          UA_ID: %s     SF_ID: %s     OS_ID: %s        VERSION: %s     \n" % \
                (lat, lon, ua_id, sf_id, os_id, version))
    output.write("%s %s %s %s %s %7.1f %7.3f %7.3f %7.0f %6.0f %6.0f %f %8.4f %7f %7f %8.2f %7.2f %7.1f %7.1f %7.1f %6.0f %7.2f %7.0f %7.0f %6.0f \n" %
                (year, month, day, j_day, hour, H, ustar, wstar, vptg, zic, zim, MOL, z0, B0, r, ws, wd, zref, temp, ztemp, ipcode, pamt, rh, pres, ccvr))
    output.close()

