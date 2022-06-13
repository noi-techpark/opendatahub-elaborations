# A22 environment: Hourly Averages

This project was formerly called "Airquality elaborations".

The original raw environmental data comes from the data collector
[environment-a22], gets aggregated by this elaboration in hourly averages.

**Table of contents**

- [A22 environment: Hourly Averages](#a22-environment-hourly-averages)
	- [Data Flow](#data-flow)
	- [Getting started](#getting-started)
		- [Prerequisites](#prerequisites)
		- [Source code](#source-code)
		- [Execute without Docker](#execute-without-docker)
		- [Execute with Docker](#execute-with-docker)
	- [Information](#information)
		- [Support](#support)
		- [Contributing](#contributing)
		- [Boilerplate](#boilerplate)
		- [Documentation](#documentation)
		- [License](#license)

## Data Flow

The flow is this:
```
a22-algorab                                      (original source)
    --> environment-a22                          (per minute with gaps; period = 60 seconds)
    --> environment-a22-averages                 (hourly; period = 3600 seconds)
```

## Getting started

These instructions will get you a copy of the project up and running
on your local machine for development and testing purposes.

### Prerequisites

To build the project, the following prerequisites must be met:

- ToDo: Check the prerequisites
- Java JDK 1.8 or higher (e.g. [OpenJDK](https://openjdk.java.net/))
- [Maven](https://maven.apache.org/) 3.x
- [PostgreSQL](https://www.postgresql.org/) 11

If you want to run the application using [Docker](https://www.docker.com/), the
environment is already set up with all dependencies for you. You only have to
install [Docker](https://www.docker.com/) and [Docker
Compose](https://docs.docker.com/compose/) and follow the instruction in the
[dedicated section](#execute-with-docker).

### Source code

Get a copy of the repository:

```bash
ToDo: git clone https://github.com/noi-techpark/project-name.git
```

Change directory:

```bash
ToDo: cd project-name/
```

### Execute without Docker

Copy the file `src/main/resources/application.properties` to
`src/main/resources/application-local.properties` and adjust the variables that
get their values from environment variables. You can take a look at the
`.env.example` for some help.

Build the project:

```bash
mvn -Dspring.profiles.active=local clean install
```

Run external dependencies, such as the database:

```
docker-compose -f docker-compose.dependencies.yml up --detach
```

Run the project:

```bash
mvn -Dspring.profiles.active=local spring-boot:run
```

The service will be available at localhost and your specified server port.

To execute the test you can run the following command:

```bash
mvn clean test
```

### Execute with Docker

Copy the file `.env.example` to `.env` and adjust the configuration parameters.

Then you can start the application using the following command:

```bash
docker-compose up
```

The service will be available at localhost and your specified server port.

To execute the test you can run the following command:

```bash
docker-compose run --rm app mvn clean test
```

## Information

### Support

For support, please contact [help@opendatahub.bz.it](mailto:help@opendatahub.bz.it).

### Contributing

If you'd like to contribute, please follow our [Getting
Started](https://github.com/noi-techpark/odh-docs/wiki/Contributor-Guidelines:-Getting-started)
instructions.

### Boilerplate

The project uses this boilerplate:
[https://github.com/noi-techpark/java-boilerplate](https://github.com/noi-techpark/java-boilerplate).

### Documentation

More documentation can be found at
[https://docs.opendatahub.bz.it](https://docs.opendatahub.bz.it).

### License

The code in this project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE
Version 3 license. See the [LICENSE](../LICENSE) file for more information.
