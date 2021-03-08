from oauth2client import client
from googleapiclient.discovery import build

from main import config


def get_google_service():
    refresh_token = config["GOOGLE_AUTH"]["refresh_token"]
    client_id = config["GOOGLE_AUTH"]["client_id"]
    client_secret = config["GOOGLE_AUTH"]["client_secret"]
    token_uri = config["GOOGLE_AUTH"]["token_uri"]
    token_expiry = int(config["GOOGLE_AUTH"]["token_expiry"])
    api_name = config["GOOGLE_AUTH"]["api_name"]
    api_version = config["GOOGLE_AUTH"]["api_version"]

    credentials = client.GoogleCredentials(access_token=None,
                                           refresh_token=refresh_token,
                                           client_id=client_id,
                                           client_secret=client_secret,
                                           token_uri=token_uri,
                                           token_expiry=token_expiry,
                                           user_agent=None)

    service = build(api_name, api_version, credentials=credentials)
    return service
