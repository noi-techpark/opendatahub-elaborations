from keycloak.keycloak_openid import KeycloakOpenID
import os

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
