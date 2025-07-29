<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# A22 environment: Non-linear calibration

The goal of this  is to fetch hourly environmental data from
the Open Data Hub, process it and send it back. For a in-depth description refer
to the chapter [Details about the implementation](#details-about-the-implementation).

## Data Flow

The original raw environmental data comes from the data collector
[environment-a22], gets aggregated by [environment-a22-averages], and finally
processed by this elaboration.

The flow is this:
```
a22-algorab                                      (original source)
    --> environment-a22                          (per minute with gaps; period = 60 seconds)
    --> environment-a22-averages                 (hourly; period = 3600 seconds)
    --> environment-a22-non-linear-calibration   (uses only averages for calibrations)
```

## Configuration

### Environmental settings

To make it work you'll need to configure the following environmental variables,
like in this sample (See [.env.example](.env.example)):

```
ODH_MOBILITY_API_NINJA=https://mobility.api.opendatahub.testingmachine.eu/v2
AUTHENTICATION_SERVER=https://auth.opendatahub.testingmachine.eu/auth/
CLIENT_SECRET=******************
PROVENANCE_NAME=environment-a22-non-linear-calibration-local
PROVENANCE_VERSION=0.0.0
PROVENANCE_LINEAGE=NOI
ODH_MOBILITY_API_WRITER=https://mobility.share.opendatahub.testingmachine.eu
LOG_LEVEL=DEBUG
```

Most of these are used for the communication with the Open Data Hub.

See the corresponding [Github Action Yaml] on how to set these variables on our
staging and production environments.

### Debugging locally
```bash
# copy and customize local .env file
cp .env.example .env
# go to src folder
cd src
# setup python venv
python -m venv .venv
source .venv/bin/activate
# install requirements and debugger
pip install -r ../requirements.txt
pip install debugpy
# run using the local .env
set -o allexport; source ../.env; set +o allexport; python -m debugpy --listen 0.0.0.0:5678 --wait-for-client main.py
# connect remote debugger to localhost:5678
```

### Keycloak settings

The `CLIENT_SECRET` comes from a service account role, currently named
`odh-a22-dataprocessor` on our Keycloak servers.

The access type must be `confidential` with `Service Accounts Enabled`.

Go to `Service Account Roles` and set the following permissions under `Client
Roles`:
1) For `odh-mobility-v2`, assign role `BDP_BLC`
2) For `odh-mobility-writer`, assign role `ROLE_ADMIN`

## Details about the implementation

Please refer to the PDF [BrennerLEC_Final_Report_220125_DC14.pdf] (Italian only)
for details. It is a deliverable of the [BrennerLEC] project. Chapter 3.4
describes the calibration curves.

## Information
[Open Data Hub - Site](https://opendatahub.com)

### Support

For support, please contact [help@opendatahub.com](mailto:help@opendatahub.com).

### Contributing

If you'd like to contribute, please follow our [Getting Started] instructions.

### Documentation

More documentation can be found at
[https://docs.opendatahub.com](https://docs.opendatahub.com).


### License

The code in this project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE
Version 3 license. See the [LICENSE](../LICENSE) file for more information.

[environment-a22]: https://github.com/noi-techpark/bdp-commons/tree/main/data-collectors/environment-a22
[environment-a22-averages]: ../environment-a22-averages/
[environment-a22-non-linear-calibration]: .
[Github Action Yaml]: ../.github/workflows/ci-environment-a22-non-linear-calibration.yml
[Getting Started]: https://github.com/noi-techpark/odh-docs/wiki/Contributor-Guidelines:-Getting-started
[BrennerLEC_Final_Report_220125_DC14.pdf]: documentation/BrennerLEC_Final_Report_220125_DC14.pdf
[BrennerLEC]: https://brennerlec.life/
