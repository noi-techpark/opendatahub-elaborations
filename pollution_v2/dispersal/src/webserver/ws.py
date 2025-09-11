# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import io
import time
import zipfile

from datetime import datetime
from osgeo import gdal
import subprocess
import rasterio
import logging
import shutil
import json
import sys
import os
from typing import List

import pandas as pd
import yaml
from fastapi import FastAPI, UploadFile, File, HTTPException, Response

from common.logging import get_logging_configuration
from preprocessors.emissions import EmissionFromODH, processConcentrations
from preprocessors.meteo import MeteoFromODH, meteo2sfc

logging.config.dictConfig(get_logging_configuration("pollution-dispersal"))

logger = logging.getLogger("pollution-dispersal.webserver.ws")

app = FastAPI()

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

# Read YAML config
CONFIG_FILE = '../config.yaml'
try:
    with open(CONFIG_FILE, 'r') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    logging.error(f"Configuration file {CONFIG_FILE} not found.")
    sys.exit(1)
except yaml.YAMLError as exc:
    logging.error(f"Error reading config file: {exc}")
    sys.exit(1)

# Paths
LOG_PATH = config['paths']['log_path']
LOG_FILE = config['paths']['log_file']
INPUT_PATH_SOURCE = config['paths']['input_path_source']
INPUT_PATH_OUTPUT = config['paths']['input_path_output']
METEO_PATH = config['paths']['meteo_path']
OUTPUT_BASE_PATH_PYTHON = config['paths']['output_base_path_python']
OUTPUT_BASE_PATH_RLINE = config['paths']['output_base_path_rline']
RLINE_INPUT_FILE = config['paths']['rline_input_file']
RLINE_EXECUTABLE = config['paths']['rline_executable']

# Log configuration
os.makedirs(LOG_PATH, exist_ok=True)
log_file = os.path.join(LOG_PATH, LOG_FILE)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()
    ]
)


# -----------------------------------------------------------------------------
# FUNCTIONS
# -----------------------------------------------------------------------------

def current_milli_time():
    return round(time.time() * 1000)

def get_domain(domains):
    """
    Filter enabled domains from the list of domains in config.yaml.

    Parameters:
    domains (list): A list of dictionaries, where each dictionary represents a domain.
                   Each domain dictionary contains an 'enabled' key, which is a boolean indicating
                   whether the domain is enabled or not.

    Returns:
    list: A list of dictionaries representing the enabled domains.
    """
    return [domain for domain in domains if domain['enabled']]


def update_rline_control_file(output_folder, input_path, ID):
    """
    Update the RLINE control file in-place with specific paths for the current domain.

    This function modifies the RLINE control file by updating specific lines with
    new file paths based on the provided parameters.

    Parameters:
    output_folder (str): The path to the output folder where RLINE results will be saved.
    input_path (str): The base path for input files (source and receptor).
    ID (str): The identifier for the current domain, used in file naming.

    Returns:
    None

    Note:
    This function assumes that the global variable RLINE_INPUT_FILE is defined
    and points to the location of the RLINE control file.
    """
    lines_to_update = {
        2: f"'{input_path}source/source_{str(ID)}.txt'\n",
        6: f"'{input_path}receptor/receptor_{str(ID)}.txt'\n",
        12: f"'{output_folder}/output_{str(ID)}.csv'\n"
    }

    with open(RLINE_INPUT_FILE, 'r') as f:
        lines = f.readlines()

    for line_index, new_value in lines_to_update.items():
        lines[line_index] = new_value
    with open(RLINE_INPUT_FILE, 'w') as f:
        f.writelines(lines)

def nearest_concentration(raster_path, x, y):
    """
    Extracts the value from band 1 of the raster at the cell nearest to a specific point.

    This function opens a GeoTIFF raster file, finds the cell closest to the given
    coordinates, and returns the value at that cell from the first band of the raster.

    Parameters:
    raster_path (str): Path to the GeoTIFF file.
    x (float): X-coordinate of the point of interest.
    y (float): Y-coordinate of the point of interest.
    Returns:
    float or None: The extracted value at the specified point, rounded to 2 decimal places.
                   Returns None if no value is found.
    """
    with rasterio.open(raster_path) as src:
        row, col = src.index(x, y)
        value = src.read(1, window=((row, row+1), (col, col+1)))
        if value.size > 0:
            return round(float(value[0][0]),2)
        else:
            return None

def get_POI_conc_values(raster_path, domain_ID, POI, POI_metadata):
    """
    Extract concentration values for Points of Interest (POI) from a raster file.

    This function processes a list of POIs, extracts concentration values from a raster file
    for each point, and appends the results to a list of POI dictionaries.

    Parameters:
    raster_path (str): The path to the raster file, without the '.tif' extension.
    domain_ID (str): The ID of the current domain.
    POI (list): A list to store dictionaries of POI information and concentration values.
    POI_metadata (list): A list of POI metadata, where each item is expected to be a list
                         containing [point_id, distance_from_source, x_coordinate, y_coordinate].

    Returns:
    list: The updated POI list with concentration values added for each point.
    """
    for point in POI_metadata:
        POI.append({
            'domain_id': int(domain_ID),
            'point_id': point[0],
            'dist_from_source_[m]': point[1],
            'x': point[2],
            'y': point[3],
            'conc_value_[ug/m3]': nearest_concentration(f'{raster_path}.tif', point[2], point[3])
        })
    return POI


def zip_folder(folder_path):
    zip_filename = "archive.zip"
    # Create a ZipFile object
    s = io.BytesIO()
    with zipfile.ZipFile(s, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Create the complete file path
                file_path = os.path.join(root, file)
                # Add file to the zip file
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

        # Must close zip for all contents to be written
        zipf.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        resp = Response(s.getvalue(), media_type="application/x-zip-compressed", headers={
            'Content-Disposition': f'attachment;filename={zip_filename}'
        })

        headers = {"Content-Disposition": "attachment; filename=files.zip"}
        return Response(s.getvalue(), headers=headers, media_type="application/zip")


@app.get("/")
def read_root():
    logging.info("Root endpoint accessed")
    return {"Hello": "World"}


@app.get("/get_capabilities/")
async def get_capabilities():

    try:
        # Domains list
        enabled_domains = get_domain(config['domains'])

        mapping = {}
        for domain in enabled_domains:
            id = domain['id']
            traffic_station_id = domain['traffic']['station_id']
            weather_station_id = domain['weather']['station_id']
            mapping[id] = {
                "description": domain['description'],
                "traffic_station_id": traffic_station_id,
                "weather_station_id": weather_station_id
            }

        return mapping
    except Exception as e:
        logging.error("Error getting capabilities", e)
        raise HTTPException(status_code=500, detail="Error getting capabilities")


@app.post("/process/")
async def process(dt: str, files: List[UploadFile] = File(...)):

    logging.info(f"invoking process with 'dt' = '{dt}'")

    dt = datetime.strptime(dt, '%Y-%m-%d-%H')
    POI_list = []
    tif_list = []

    # Domains list
    enabled_domains = get_domain(config['domains'])

    # Timespan
    start_datetime = dt - pd.Timedelta(minutes=59)
    end_datetime = dt

    try:
        with files[0].file as emissions_file:
            emission_content = emissions_file.read().decode()
            emission_df = EmissionFromODH(enabled_domains, start_datetime, end_datetime, csv_content=emission_content)
    except Exception as e:
        logging.error("Error reading emission file", e)
        raise HTTPException(status_code=500, detail="Error reading emission file")

    try:
        with files[1].file as meteo_file:
            meteo_content = meteo_file.read().decode()
            meteo_df = MeteoFromODH(enabled_domains, start_datetime, end_datetime, csv_content=meteo_content)
    except Exception as e:
        logging.error("Error reading meteo file", e)
        raise HTTPException(status_code=500, detail="Error reading meteo file")

    now = current_milli_time()

    main_output_folder_python = f'{OUTPUT_BASE_PATH_PYTHON}{now}/'
    os.makedirs(main_output_folder_python, exist_ok=True)

    main_output_file_python = f'{main_output_folder_python}output'
    vrt_filename = f'{main_output_folder_python}{config["paths"]["vrt_file"]}'
    poi_filename = f'{main_output_folder_python}{config["paths"]["POI_output_file"]}'

    logging.info(f"ready to write on {main_output_file_python}")
    logging.info(f"ready to write on {vrt_filename}")
    logging.info(f"ready to write on {poi_filename}")

    main_output_folder_rline = f'{OUTPUT_BASE_PATH_RLINE}{now}/'

    for domain in enabled_domains:

        ID = str(domain['id'])
        description = domain['description']
        weather_station_type = domain['weather']['station_type']
        weather_station_id = domain['weather']['station_id']
        traffic_station_id = domain['traffic']['station_id']
        POI_data = domain['POI']
        source_file = INPUT_PATH_SOURCE + 'source/' + domain['source']
        receptor_file = INPUT_PATH_SOURCE + 'receptor/' + domain['receptor']
        station_output_folder_python = f'{main_output_folder_python}{ID}'
        if not os.path.exists(station_output_folder_python):
            os.makedirs(station_output_folder_python)
        station_output_folder_rline = f'{main_output_folder_rline}{ID}'
        station_output_file_python = station_output_folder_python + f'/output_{ID}'
        os.makedirs(station_output_folder_python, exist_ok=True)

        # write log info
        logging.info(f'===========================================================')
        logging.info(f'{ID}) {description}')
        logging.info(f'INPUT - Timespan: {start_datetime} - {end_datetime}')
        logging.info(f'INPUT - Weather station: {weather_station_type} {weather_station_id}')
        logging.info(f'INPUT - Traffic station: {traffic_station_id}')

        # check if receptor and source file exist
        if not os.path.isfile(source_file):
            logging.error(f"Source file {source_file} not found")
            continue
        # check on python (that's why the replace) if receptor file exists (to be used in rline)
        if not os.path.isfile(receptor_file):
            logging.error(f"Receptor file {receptor_file} not found")
            continue

        # process meteo data for the current domain and create meteo.sfc file
        try:
            domain_meteo_df = meteo_df[meteo_df['station-id'].astype(str) == str(weather_station_id)]

            if not domain_meteo_df.empty:
                meteo2sfc(domain_meteo_df, METEO_PATH)
                logging.info(f"DONE - Meteo data processed")
            else:
                logging.error(f"No meteo data found for station {weather_station_type} {weather_station_id}")
                continue
        except Exception as e:
            logging.error(f"Error processing meteo data", e)
            continue

        # update Line_Source_Inputs.txt
        try:
            update_rline_control_file(station_output_folder_rline, INPUT_PATH_OUTPUT, ID)
            logging.info(f"DONE - RLINE control file updated")
        except Exception as e:
            logging.error(f"Error updating RLINE control file", e)
            continue

        # run RLINE
        try:
            subprocess.run(RLINE_EXECUTABLE, cwd="..", check=True)
            logging.info("DONE - RLINE simulation executed")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error during RLINE execution", e)
            continue

        # process concentrations data for the current domain
        try:
            domain_emission_df = emission_df.loc[emission_df['station-id'] == int(traffic_station_id)]
            if not domain_emission_df.empty:
                processConcentrations(station_output_file_python, domain_emission_df)
                logging.info(f"DONE - Concentrations data processed")
            else:
                logging.error(f"No emission data found for station {traffic_station_id}")
                continue
        except Exception as e:
            logging.error(f"Error processing concentrations data", e)
            continue

        # Save file tif
        try:
            subprocess.run(['gdal_translate', '-a_srs', 'epsg:32632', '-a_nodata', '-999', '-of', 'AAIGrid',
                            f'{station_output_file_python}.xyz', f'{station_output_file_python}.tif'], check=True)
            tif_list.append(f'{station_output_file_python}.tif')
            logging.info("DONE - TIF file generated")
            # Get concentrations values from receptor POIs
            POI_list = get_POI_conc_values(station_output_file_python, ID, POI_list, POI_data)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating TIF file", e)
            continue

    # -----------------------------------------------------------------------------
    # OUTPUT
    # -----------------------------------------------------------------------------

    logging.info(f'===========================================================')
    # Write POI concentration json
    with open(poi_filename, 'w') as file:
        json.dump(POI_list, file, indent=4)
        logging.info("DONE - POI concentration json file generated")

    # If at least one tif file has been created:
    if tif_list:
        # Create virtual raster
        try:
            vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest')
            gdal.BuildVRT(vrt_filename, list(reversed(tif_list)), options=vrt_options)
            logging.info("DONE - Virtual Raster file generated")
        except Exception as e:
            logging.error(f"Error creating Virtual Raster file: {e}")

        # Save file shp
        try:
            subprocess.run(['gdal_contour', '-a', 'conc_value', '-3d', '-fl', '1', '2', '5', '10', '20', '50', '100',
                            vrt_filename, f'{main_output_file_python}.shp'], check=True)
            logging.info("DONE - SHP file generated")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating SHP file", e)
            raise HTTPException(status_code=500,
                                detail="Error creating SHP file")

        # Save file GeoJson
        try:
            subprocess.run(["ogr2ogr",
                            f'{main_output_file_python}.geojson', f'{main_output_file_python}.shp'], check=True)
            logging.info("DONE - GeoJSON file generated")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating GeoJSON file", e)
            raise HTTPException(status_code=500,
                                detail="Cannot process pollution dispersal: error creating GeoJSON file")

        res = zip_folder(main_output_folder_python)

        logging.info(f"removing {main_output_folder_python}")
        shutil.rmtree(main_output_folder_python)

        return res
