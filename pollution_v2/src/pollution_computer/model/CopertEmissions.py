# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Created on Tue Aug 16 2022
@author: nicola
"""
import logging
import os
import re
import sqlite3
from pathlib import Path

import pandas as pd
import numpy as np

logger = logging.getLogger("pollution_v2.pollution_computer.model.CopertEmissions")


def find_latest_file(path_format: str, year: int) -> str:
    try_year = year
    ret = ""
    while try_year > 2017:
        filename = path_format.format(str(try_year))
        file = Path(filename)
        if file.is_file():
            ret = filename
            break
        try_year -= 1

    if try_year < year:
        logger.warning(f"File {path_format.format(str(year))} not found. Using most recent {filename} instead")

    if ret == "":
        raise FileNotFoundError(f"Unable to find file {path_format} for year {year} or preceding")

    return ret


def find_copert_db(input_data_path: str, year: int) -> str:
    """Prefers a COPERT db named for the given year (copert<version>_<year>.db), otherwise falls back to the
    most recent unversioned-by-year db (copert<version>.db, highest version, e.g. copert510.db)."""
    directory = Path(input_data_path)

    year_matches = sorted(directory.glob(f"copert*_{year}.db"))
    if year_matches:
        return str(year_matches[-1])

    def version(file: Path):
        match = re.fullmatch(r"copert(\d+)\.db", file.name)
        return int(match.group(1)) if match else None

    candidates = [(version(f), f) for f in directory.glob("copert*.db") if version(f) is not None]
    if not candidates:
        raise FileNotFoundError(f"Unable to find a copert db in {input_data_path} for year {year}")

    _, latest = max(candidates)
    logger.warning(f"No copert db for year {year} found. Using most recent {latest.name} instead")
    return str(latest)


# stima delle emissioni con metodo di copert
def copert_emissions(traffic_df, fc_info_year: str = ""):

    # ------------------------------------------------------------------------------
    # 0. INIZIALIZZAZIONE
    # ------------------------------------------------------------------------------
    input_data_path = f"{os.path.dirname(os.path.abspath(__file__))}/input/"
    input_fc_info = find_latest_file(input_data_path + "fc_info_{}.csv", int(fc_info_year))
    input_copert = find_copert_db(input_data_path, int(fc_info_year))

    con = sqlite3.connect(input_copert)
    copert = pd.read_sql_query("SELECT * FROM COPERT", con)
    fc = pd.read_csv(input_fc_info)
    geometry = pd.read_csv(input_data_path + "geometry.csv")
    km = pd.read_csv(input_data_path + "km.csv")

    # ------------------------------------------------------------------------------
    # 1. CALCOLI PRELIMINARI
    # ------------------------------------------------------------------------------
    adt = traffic_df
    adt = pd.merge(adt, km, on="Station", how="left")
    adt["KM"] = adt["KM"].astype(float).div(1000)
    adt["KM"] = adt["KM"].fillna(adt["km"])
    adt.drop("km", axis=1, inplace=True)
    adt.rename(columns={"KM": "km"}, inplace=True)
    adt["KM"] = adt["km"].astype(float).round()

    if ("RoadSlope" in copert) and ("RoadSlope" in geometry):
        adt = pd.merge(adt, geometry[["KM", "RoadSlope"]], on="KM")
        adt.loc[(adt["Lane"] == 1) | (adt["Lane"] == 2), "RoadSlope"] = -1 * adt["RoadSlope"]
        df = pd.DataFrame(copert, columns=["Category", "RoadSlope"])
        df = df[df["RoadSlope"].isnull()].drop_duplicates()
        adt["RoadSlope"] = np.where(adt["Category"].isin(df["Category"]), float("NaN"), adt["RoadSlope"])

    emission = pd.merge(adt, fc, on=["Category"])
    emission["Total_Transits"] = emission["Transits"] * emission["PercvsADT"]

    # ------------------------------------------------------------------------------
    # 2. CALCOLO FATTORI DI EMISSIONE, EMISSIONI PER KM, EMISSIONI TOTALI
    # ------------------------------------------------------------------------------
    if ("RoadSlope" in copert) and ("RoadSlope" in geometry):
        emission = pd.merge(emission, copert, on=["Location", "Category", "Fuel", "ID_Euro", "RoadSlope"])
    elif ("RoadSlope" in copert) and ("RoadSlope" not in geometry):
        copert = copert[(copert["RoadSlope"] == 0) | (copert["RoadSlope"].isnull())]
        emission = pd.merge(emission, copert, on=["Location", "Category", "Fuel", "ID_Euro", "RoadSlope"])
    else:
        emission = pd.merge(emission, copert, on=["Location", "Category", "Fuel", "ID_Euro"])

    emission.loc[emission["Speed"] < emission["MinSpeed"], "Speed"] = emission["MinSpeed"]
    emission.loc[emission["Speed"] > emission["MaxSpeed"], "Speed"] = emission["MaxSpeed"]

    emission["EF"] = (
        (emission["Alpha"] * emission["Speed"] ** 2 + emission["Beta"] * emission["Speed"] + emission["Gamma"]
         + emission["Delta"] / emission["Speed"])
        / (emission["Epsilon"] * emission["Speed"] ** 2 + emission["Zita"] * emission["Speed"] + emission["Hta"])
        * (1.0 - emission["EuroReductionFactor"])
        * (1.0 - emission["FuelReductionFactor"])
    )
    emission["E"] = emission["EF"] * emission["Total_Transits"]

    emission_agg = emission.groupby(
        ["date", "time", "Period", "Location", "Station", "Lane", "Category", "km", "Pollutant"]
    ).agg({"Total_Transits": sum, "E": sum}).reset_index()

    emission_agg["Total_Transits"] = emission_agg["Total_Transits"].round().astype(int)

    # ------------------------------------------------------------------------------
    # 3. ESPORTAZIONE RISULTATI
    # ------------------------------------------------------------------------------
    return emission_agg[["date", "time", "Period", "Location", "Station", "Lane", "Category", "km", "Pollutant",
                          "Total_Transits", "E"]]
