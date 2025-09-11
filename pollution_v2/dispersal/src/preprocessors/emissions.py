# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from io import StringIO

import pandas as pd
import sys
import os

def EmissionFromODH(enabled_domains, start_datetime, end_datetime, csv_content: str = None):

    """
    TODO U-HOPPER: Implement this function to fetch emissions data from ODH.
    La funzione deve restituire un dataframe con la stessa struttura e campi del csv di esempio './data/input/emissions/df_emissions_example.csv'.
    Per il momento consideriamo solo l'inquinante NOx.
    Il dato fornito deve essere comprensivo delle emissioni di tutte le corsie della stazione.
    'enabled_domains' è la lista contenente tutte le informazioni di config.yaml per i domini abilitati da cui ricavare tipo e id della sorgente dati.
    start_datetime (definito come argomento al main.py) e end_datetime (start_datetime + 1h) definiscono l'intervallo temporale da considerare, sono nel formato YYYY-mm-dd HH:MM:SS
    """

    if csv_content:
        csv = StringIO(csv_content)
    else:
        # Questo è solo un dataset di esempio per far girare il codice
        csv = StringIO('../data/input/emissions/df_emissions_example.csv')

    df = pd.read_csv(csv)
    return df

def processConcentrations(rline_output_path, emission_df):
    emiss_coeff = emission_df[['light_vehicles', 'heavy_vehicles', 'buses']].sum().sum()/3600/1000  # emissioni in g/(m*s)
    rline_output = pd.read_csv(rline_output_path + '.csv', skiprows=11, skipinitialspace=True)
    rline_output['C_A22'] = rline_output['C_A22']*emiss_coeff
    rline_output.replace([float('nan'), float('inf'), -float('inf')], -999, inplace=True)

    # save csv file
    rline_output.to_csv(rline_output_path + '.csv', index=False)

    # save xyz file
    rline_output.iloc[:, [3, 4, 6]].to_csv(rline_output_path + '.xyz', sep=' ', index=False, header=False)
