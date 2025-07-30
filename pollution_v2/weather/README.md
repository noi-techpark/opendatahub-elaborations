<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# Raod Weather

Il calcolo delle previsioni di condizione stradale si basa sul modello METRo ([qui la wiki](https://framagit.org/metroprojects/metro/-/wikis/METRo)).
METRo deve essere alimentato da alcuni files xml di input (observations, forecast, parameters) e produce un file xml di output (roadcast).

## Getting started

Tutti i file del modello METRo sono inclusi nella cartella *./metro*. Se dovesse essere necessaria un'installazione pulita del modello fare riferimento a [questa pagina](https://framagit.org/metroprojects/metro/-/wikis/Installation_(METRo)) della wiki.

Compatilibità versioni Python:

```Python 3.10```

Installare le dipendenze per Python:

```pip install -r requirements.txt```

## Run

Dalla cartella principale eseguire il comando:

```python main.py <station_code>```

Dove `<station_code>` è il codice della stazione road weather (101, 102, 103, 104, ...).
L'output viene generato in *./data/roadcast/*.

## Run in a Docker container

To execute the algorithm in a Docker container, first create an image on the basis of the provided Dockerfile:

```docker build -t road_weather --platform=linux/amd64 --no-cache --progress=plain .```

Then create a container based on the image.

```docker run -d -it --name rwtest_v2 -p 80:80 road_weather```

Activate container shell.

```docker exec -it rwtest_v2 /bin/sh```

Execute METRo test execution.

```python3 /usr/local/metro/usr/bin/metro --selftest```
