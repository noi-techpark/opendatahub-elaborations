<!--
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

SPDX-License-Identifier: CC0-1.0
-->

# Metadata API automatic fill

## Datasets Metadata Script Summary

A script that runs regularly to extract the latest information from the Open Data Hub APIs (at the moment only Content APIs) and put it in the MetaData API. 

The fields in the Metadata API that are updated by the script are:

- **Sources**: list of data providers for the dataset
- **LicenseInformation**: list of licenses included in the dataset
- **RecordCount**: total records in the dataset
  

