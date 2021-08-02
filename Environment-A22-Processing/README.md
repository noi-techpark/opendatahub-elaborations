A22 environment data processing
================================

the goal of this tool is to fetch hourly environmental data from odh, process it and send the data back to odh.
It can be called by a single function and therefore easily used as a lambda function.
To make it work you'll need to configure the following environmental variables, like in this sample:

```
RAW_DATA_ENDPOINT=https://mobility.api.opendatahub.testingmachine.eu/v2
AUTHENTICATION_SERVER=https://auth.opendatahub.testingmachine.eu/auth/
CLIENT_SECRET=******************
PROVENANCE_NAME=local
PROVENANCE_VERSION=0.1.0
PROVENANCE_LINEAGE=odh
ODH_SHARE_ENDPOINT=https://share.opendatahub.testingmachine.eu
LOG_LEVEL=DEBUG
```

Most of these are used for the communication to opendatahub. You'll need to request an client from odh stuff which has ADMIN permissions on the writer side and the role 'BLC' on the API side.
