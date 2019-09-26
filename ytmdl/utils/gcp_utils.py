import json
import os

import googleapiclient.discovery
import googleapiclient.errors
from firebase_admin import credentials
from oauth2client import file, tools, client

from ytmdl import const
from ytmdl.const import LOCAL_SERVICE_SECRETS
from ytmdl.utils.io_utils import safe_open

SCOPE_MAP = {
    "youtube": ["https://www.googleapis.com/auth/youtube.readonly"],
    "drive": ["https://www.googleapis.com/auth/drive.file"]
}


def is_cloud():
    return 'GCP_PROJECT' in os.environ


def get_service_creds():
    if is_cloud():
        return credentials.ApplicationDefault()
    else:
        assert os.path.exists(LOCAL_SERVICE_SECRETS)
        return credentials.Certificate(LOCAL_SERVICE_SECRETS)


def _get_token_path(service_name, service_version):
    return os.path.join(const.TMP_PATH, service_name + service_version + "token.json")


def get_service_object(service_name, service_version, token):
    token_path = _get_token_path(service_name, service_version)
    store = file.Storage(token_path)
    type_match_success = True
    with safe_open(token_path, 'w') as fp:
        if isinstance(token, dict):
            json.dump(token, fp)
        elif isinstance(token, str):
            fp.write(token)
        else:
            type_match_success = False

    if not type_match_success:
        raise RuntimeError("'token' is neither a dict or a str")

    return googleapiclient.discovery.build(service_name, service_version, credentials=store.get())


def authenticate(service_name, service_version, secrets_path):
    token_path = _get_token_path(service_name, service_version)
    store = file.Storage(token_path)
    flow = client.flow_from_clientsecrets(secrets_path, SCOPE_MAP[service_name.lower()])
    creds = tools.run_flow(flow, store)

    googleapiclient.discovery.build(service_name, service_version, credentials=creds)

    return token_path
