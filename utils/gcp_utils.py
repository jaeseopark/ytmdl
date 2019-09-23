import os

from firebase_admin import credentials

from const import LOCAL_SERVICE_SECRETS


def is_cloud():
    return 'GCP_PROJECT' in os.environ


def get_service_creds():
    if is_cloud():
        return credentials.ApplicationDefault()
    else:
        assert os.path.exists(LOCAL_SERVICE_SECRETS)
        return credentials.Certificate(LOCAL_SERVICE_SECRETS)
