# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import time
from keycloak.keycloak_openid import KeycloakOpenID

# Configure client

keycloak_openid = (KeycloakOpenID(server_url= os.getenv("AUTHENTICATION_SERVER"),
                    client_id="odh-a22-dataprocessor",
                    realm_name="noi",
                    client_secret_key=os.getenv("CLIENT_SECRET"),
                    verify=True))

class KeycloakClient:

    @staticmethod
    def getDefaultInstance():
        return keycloak_openid


class TokenManager:
    """Caches a client_credentials token and refetches it once it's close
    to expiry, instead of a caller holding onto a single token forever."""

    # Refresh this many seconds before actual expiry to avoid edge-of-life 401s
    EXPIRY_MARGIN_SEC = 30

    def __init__(self):
        self._client = KeycloakClient.getDefaultInstance()
        self._token = None
        self._expires_at = 0

    def get_access_token(self):
        if self._token is None or time.time() >= self._expires_at:
            self._token = self._client.token("", "", "client_credentials")
            self._expires_at = time.time() + self._token["expires_in"] - self.EXPIRY_MARGIN_SEC
        return self._token["access_token"]
