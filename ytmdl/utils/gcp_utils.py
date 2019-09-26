import json
import os

import googleapiclient.discovery
import googleapiclient.errors
from firebase_admin import credentials
from oauth2client import file

from ytmdl import const
from ytmdl.const import LOCAL_SERVICE_SECRETS
from ytmdl.utils.io_utils import safe_open

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def is_cloud():
    return 'GCP_PROJECT' in os.environ


def get_service_creds():
    if is_cloud():
        return credentials.ApplicationDefault()
    else:
        assert os.path.exists(LOCAL_SERVICE_SECRETS)
        return credentials.Certificate(LOCAL_SERVICE_SECRETS)


def get_service_object(service_name, service_version, token):
    token_path = os.path.join(const.TMP_PATH, "token.json")
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

# TODO: registration
# def _lazy_init_clint_secrets(secrets_path):
#     if not os.path.exists(secrets_path):
#         config_dict_ref = firestore.find(const.FIRESTORE_APP, const.FIRESTORE_APP_CONFIG)
#         config_dict = firestore.to_dict(config_dict_ref)
#         client_secrets_str = config_dict[const.FIRESTORE_APP_CONFIG_KEY_CLIENT_SECRETS]
#         with safe_open(secrets_path, 'w') as fp:
#             fp.write(client_secrets_str)
# def authenticate(service, service_version):
#     secrets_path = '/tmp/ytmdl/client_secrets.json'
#     _lazy_init_clint_secrets(secrets_path)
#     flow = client.flow_from_clientsecrets(secrets_path, SCOPES)
#     creds = tools.run_flow(flow, store)
#
#     with safe_open(token_path) as fp:
#         token_str = fp.read()
#         user_ref.set({const.FIRESTORE_USERS_KEY_TOKEN: token_str})
#
#     return googleapiclient.discovery.build(service, version, credentials=creds)
