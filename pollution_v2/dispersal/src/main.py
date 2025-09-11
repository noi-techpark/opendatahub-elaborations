# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime
from osgeo import gdal
import pandas as pd
import subprocess
import rasterio
import argparse
import logging
import shutil
import json
import yaml
import sys
import os

from preprocessors.emissions import EmissionFromODH, processConcentrations
from preprocessors.meteo import MeteoFromODH, meteo2sfc

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

OUTPUT_FILENAME = OUTPUT_BASE_PATH_PYTHON + config['paths']['output_filename']
VRT_PATH = OUTPUT_BASE_PATH_PYTHON + config['paths']['vrt_file']
POI_PATH = OUTPUT_BASE_PATH_PYTHON + config['paths']['POI_output_file']

# Folders
shutil.rmtree(OUTPUT_BASE_PATH_PYTHON)
os.makedirs(OUTPUT_BASE_PATH_PYTHON, exist_ok=True)

# Lists
POI_list = []
tif_list = []

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

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run RLINE simulation for different domains')
parser.add_argument('-dt', type=lambda d: datetime.strptime(d, '%Y-%m-%d %H'),
                    help='The start date and time of the simulation - format YYYY-MM-DD HH', required=True)
args = parser.parse_args()

# Domains list
enabled_domains = get_domain(config['domains'])

# Timespan
start_datetime = args.dt - pd.Timedelta(minutes=59)
end_datetime = args.dt

# Download meteo data from ODH
meteo_df = MeteoFromODH(enabled_domains, start_datetime, end_datetime)

# Download emission data from ODH
emission_df = EmissionFromODH(enabled_domains, start_datetime, end_datetime)


for domain in enabled_domains:
    ID = str(domain['id'])
    description = domain['description']
    weather_station_type = domain['weather']['station_type']
    weather_station_id = domain['weather']['station_id']
    traffic_station_id = domain['traffic']['station_id']
    POI_data = domain['POI']
    source_file = INPUT_PATH_SOURCE + 'source/' + domain['source']
    receptor_file = INPUT_PATH_OUTPUT + 'receptor/' + domain['receptor']
    output_folder_python = f'{OUTPUT_BASE_PATH_PYTHON}{ID}'
    output_folder_rline = f'{OUTPUT_BASE_PATH_RLINE}{ID}'
    output_file_python = output_folder_python + f'/output_{ID}'

    # create output folder
    os.makedirs(output_folder_python, exist_ok=True)

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
    if not os.path.isfile(receptor_file.replace(INPUT_PATH_OUTPUT, INPUT_PATH_SOURCE)):
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
        logging.error(f"Error processing meteo data: {e}")
        continue

    # update Line_Source_Inputs.txt
    try:
        update_rline_control_file(output_folder_rline, INPUT_PATH_OUTPUT, ID)
        logging.info(f"DONE - RLINE control file updated")
    except Exception as e:
        logging.error(f"Error updating RLINE control file: {e}")
        continue

    # run RLINE
    try:
        subprocess.run(RLINE_EXECUTABLE, cwd="..", check=True)
        logging.info("DONE - RLINE simulation executed")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during RLINE execution: {e}")
        continue

    # process concentrations data for the current domain
    try:
        domain_emission_df = emission_df.loc[emission_df['station-id'] == int(traffic_station_id)]
        if not domain_emission_df.empty:
            processConcentrations(output_file_python, domain_emission_df)
            logging.info(f"DONE - Concentrations data processed")
        else:
            logging.error(f"No emission data found for station {traffic_station_id}")
            continue
    except Exception as e:
        logging.error(f"Error processing concentrations data: {e}")
        continue

    # Save file tif
    try:
        subprocess.run(['gdal_translate', '-a_srs', 'epsg:32632', '-a_nodata', '-999', '-of', 'AAIGrid',
                        f'{output_file_python}.xyz', f'{output_file_python}.tif'], check=True)
        tif_list.append(f'{output_file_python}.tif')
        logging.info("DONE - TIF file generated")
        # Get concentrations values from receptor POIs
        POI_list = get_POI_conc_values(output_file_python, ID, POI_list, POI_data)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error creating TIF file: {e}")
        continue

# -----------------------------------------------------------------------------
# OUTPUT
# -----------------------------------------------------------------------------

logging.info(f'===========================================================')
# Write POI concentration json
with open(POI_PATH, 'w') as file:
    json.dump(POI_list, file, indent=4)
    logging.info("DONE - POI concentration json file generated")

# If at least one tif file has been created:
if tif_list:
    # Create virtual raster
    try:
        vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest')
        vrt = gdal.BuildVRT(VRT_PATH, list(reversed(tif_list)), options=vrt_options)
        vrt = None
        logging.info("DONE - Virtual Raster file generated")
    except Exception as e:
        logging.error(f"Error creating Virtual Raster file: {e}")

    # Save file shp
    try:
        subprocess.run(['gdal_contour', '-a', 'conc_value', '-3d', '-fl', '1', '2', '5', '10', '20', '50', '100',
                        VRT_PATH, f'{OUTPUT_FILENAME}.shp'], check=True)
        logging.info("DONE - SHP file generated")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error creating SHP file: {e}")

    # Save file GeoJson
    try:
        subprocess.run(["ogr2ogr",
                        f'{OUTPUT_FILENAME}.geojson', f'{OUTPUT_FILENAME}.shp'], check=True)
        logging.info("DONE - GeoJSON file generated")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error creating GeoJSON file: {e}")
