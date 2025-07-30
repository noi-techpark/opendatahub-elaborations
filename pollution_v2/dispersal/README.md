<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# ODH Pollution dispersion

## Descrizione

Questo progetto esegue simulazioni di dispersione degli inquinanti emessi in atmosfera dall'autostrada A22 usando il modello gfortran.

Ogni simulazione è svolta a scala oraria sui domini autostradali definiti anticipatamente.
Il calcolo viene svolto in serie sui domini. Per ogni dominio di calcolo vengono eseguite le seguenti operazioni:

1. lettura del file `config.yaml`
   1. definizione dei path di input (source.txt e receptor.txt) e output.csv
   2. definizione delle stazioni meteo e traffico associate al dominio
2. processing dei dati meteo, scrittura dei dati nel file `./data/input/meteo/meteo.sfc` (il contenuto del file viene sovrascritto ad ogni run)
3. update del file `Line_Source_Inputs.txt` contenente le informazioni necessarie per la simulazione RLINE
4. run RLINE
5. processing dei dati di emissione, necessari a scalare l'output di concentrazioni di RLINE
6. creazione dei file .tif, .shp, .kml, .geojson

I dati meteo e di emissione vengono scaricati una volta per tutti i domini all'avvio del programma.

**Nella repository sono presenti solamente i file source e receptor relativi al tratto _Bolzano Nord - Bolzano Sud_ (ID: 6), pertanto per la fase di sviluppo può essere eseguito l'intero processo solamente su questo dominio.**

## Configurazione

Il file `config.yaml` contiene i seguenti tag:
- `paths`: Definizione dei percorsi per i file di input e output.
- `domains`: Definizione dei domini autostradali. Ogni dominio è definito da:
  - **id**: identificativo del dominio.
  - **enabled**: flag per abilitare o meno la simulazione per il dominio.
  - **description**: nome del dominio.
  - **source**: nome del file che definisce la geometria della sorgente emissiva (statico).
  - **receptor**: nome del file che definisce la geometria dei recettori (statico).
  - **output**: nome del file di output di RLINE.
  - **weather/station_type**: tipo di stazione meteorologica (RoadWeather o Weather).
  - **weather/station_id**: identificativo della stazione meteorologica.
  - **traffic/station_id**: identificativo della stazione traffico per i dati delle emissioni.

Lo script principale `main.py` esegue il calcolo per tutti i domini definiti e abilitati (`enabled = True`) nel file `config.yaml`

## Output

- `POI.json`: un json che contiene il valore di concentrazione calcolato in specifici punti (definiti nel file config.yaml)
- `virtual_raster.vrt`: file di definizione del virtual raster che unisce i geotiff generati su ogni dominio.
- `concentration_contouring.shp`: contouring dei valori di concentrazione in formato shp.
- `concentration_contouring.kml`: contouring in formato kml.
- `concentration_contouring.geojson`: contouring in formato geojson.

## Run

```
python main.py -dt [YYYY-MM-DD HH]
```
`[YYYY-MM-DD HH]` è la data ora relativa alla simulazione. Ad esempio:

```
python main.py -dt '2024-11-01 08'
```

avvia la simulazione in serie su tutti i domini abilitati relativi alla data e ora specificata. Di fatto esegue le simulazioni considerando i dati meteorologici ed emissivi compresi tra le 07:00 e le 08:00 del 2024-11-01.

## Run in a Docker container

To execute the algorithm in a Docker container, first create an image on the basis of the provided Dockerfile:

```docker build -t pollution_dispersal --platform=linux/amd64 --no-cache --progress=plain .```

Then create a container based on the image.

```docker run -d -it --name pdtest -p 80:80 pollution_dispersal```

Activate container shell.

```docker exec -it pdtest /bin/sh```

Execute METRo test execution.

```python3 main.py -dt "2024-11-01 08"```

## Invoke WS endpoint

Retrieve the mapping between traffic stations and weather stations.

```
curl --location 'http://localhost:80/get_capabilities/'
```

Make the following POST request to get a ZIP file containing all the outputs.

```
curl --location 'http://localhost:80/process/?station_code=684&dt=2024-11-01-08' \
     --form 'files=@"/Users/marcoangheben/Work/aiaas/pollution-dispersal/data/input/emissions/df_emissions_example.csv"' \
     --form 'files=@"/Users/marcoangheben/Work/aiaas/pollution-dispersal/data/input/meteo/df_meteo_example.csv"'
```
