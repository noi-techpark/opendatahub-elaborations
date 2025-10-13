#!/bin/bash

# SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

response=$(curl -s 'https://auth.opendatahub.com/auth/realms/noi/protocol/openid-connect/token' \
  -X POST \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "grant_type=client_credentials" \
  --data-urlencode "client_id=$OAUTH_CLIENT_ID" \
  --data-urlencode "client_secret=$OAUTH_CLIENT_SECRET" \
) 
echo $response | jq -r '.access_token'