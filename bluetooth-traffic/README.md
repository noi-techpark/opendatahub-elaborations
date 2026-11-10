<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# BluetoothTrafficElaboration
Application which takes vehicular traffic data from the big data platform,
collected by bluetoothboxes around the city of Bolzano, and makes different
elaborations and saving them back to the bdp again.

[![CI](https://github.com/noi-techpark/BluetoothTrafficElaboration/actions/workflows/ci.yml/badge.svg)](https://github.com/noi-techpark/BluetoothTrafficElaboration/actions/workflows/ci.yml)


**Table of contents**
- [BluetoothTrafficElaboration](#bluetoothtrafficelaboration)
	- [Getting started](#getting-started)
		- [Prerequisites](#prerequisites)
		- [Source code](#source-code)
		- [Build](#build)
	- [Running tests](#running-tests)
	- [Deployment](#deployment)
		- [Configure Elaborations/Tasks](#configure-elaborationstasks)
	- [Information](#information)
		- [Support](#support)
		- [Contributing](#contributing)
		- [Documentation](#documentation)
		- [License](#license)


## Getting started

These instructions will get you a copy of the project up and running
on your local machine for development and testing purposes.

### Prerequisites

To build the project, the following prerequisites must be met:

- Java JDK 1.8 or higher (e.g. [OpenJDK](https://openjdk.java.net/))
- [Maven](https://maven.apache.org/) 3.x
- A postgres database with the schema intimev2 and elaboration (bdp) already
  installed

### Source code

Get a copy of the repository:

```bash
git clone https://github.com/noi-techpark/BluetoothTrafficElaboration
```

Change directory:

```bash
cd BluetoothTrafficElaboration/
```

### Build

Build the project:

```bash
mvn clean package
```

## Running tests

The unit tests can be executed with the following command:

```bash
mvn clean test
```

## Deployment

This is a plain Java 21 application (no application server). `mvn clean package`
produces the executable `target/app.jar`, which runs all elaborations once and
exits. In k8s it is run every full hour by a CronJob (`infrastructure/helm`).

Steps:

* connect to the postgres database and execute the following script that will
  add the intimev2.deltart function to an existing bdp database

```bash
psql ... < BluetoothTrafficElaboration/deltart.sql
```

* set the environment variable `JDBC_URL` to the jdbc url that connects to the
  postgres database (the CI injects it as a secret)

```
JDBC_URL=jdbc:postgresql://host:port/db?user=...&password=...
```

* run it, locally or in a container (see `infrastructure/docker/Dockerfile`)

```bash
java -jar target/app.jar
```

Progress and results are logged to stdout and stored in the tables
`scheduler_task` and `scheduler_run`.

### Configure Elaborations/Tasks

Elaborations can be configured in table **scheduler_task**.

Required columns:

- **application_name**: `vtraffic/plugin\_cs\_monitor`
- **task_name**       : descriptive name of the task for human
- **function_name**   : the function used for the elaboration. valid values are listed below
- **args**            : period/window of the elaboration in seconds (600 = 10min)
- **calc_order**      : if null elaboration is skipped. If a number it is used
  to order elaborations sequentially (order is important because elaborations
  may have dependencies)
- **enabled**         : `T`
- **status**          : `QUEUED`

valid function_name values are:

compute\_bspeed
compute\_bspeed\_100kmh
count\_bluetooth\_intime
count\_match\_intime
create\_bluetooth\_lhv
create\_matches
run\_mode\_intime
run\_mode\_intime\_100kmh

Here an example sql statement on how to add a new elaboration (please modify values before execution):

```sql
insert into scheduler_task (application_name,             task_name,          function_name,            args, calc_order, enabled, status)
                    values ('vtraffic/plugin_cs_monitor', 'descriptive name', 'count_bluetooth_intime',   60,          1, 'T',     'QUEUED');

insert into scheduler_task (application_name,             task_name,          function_name,            args, calc_order, enabled, status)
                    values ('vtraffic/plugin_cs_monitor', 'Bluetooth Elapsed time greater than 100 km/h', 'run_mode_intime_100kmh',   600,       99998, 'T',     'QUEUED');

insert into scheduler_task (application_name,             task_name,          function_name,            args, calc_order, enabled, status)
                    values ('vtraffic/plugin_cs_monitor', 'speed greater than 100 km/h', 'compute_bspeed_100kmh',   600,       99999, 'T',     'QUEUED');


```

## Information

### Support

For support, please contact [help@opendatahub.com](mailto:help@opendatahub.com).

### Contributing

If you'd like to contribute, please follow our [Getting
Started](https://github.com/noi-techpark/odh-docs/wiki/Contributor-Guidelines:-Getting-started)
instructions.

### Documentation

More documentation can be found at
[https://docs.opendatahub.com](https://docs.opendatahub.com).

### License

The code in this project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE
Version 3 license. See the [LICENSE](../LICENSE) file for more information.
