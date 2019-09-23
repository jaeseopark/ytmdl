import json
import os

import googleapiclient.discovery
import googleapiclient.errors
from oauth2client import file, client, tools

import const
import firestore

from utils.io_utils import safe_open

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/drive.file"]


def _lazy_init_clint_secrets(secrets_path):
    if not os.path.exists(secrets_path):
        client_secrets = json.loads(firestore.get(const.FIRESTORE_APP, const.FIRESTORE_APP_CONFIG)[const.FIRESTORE_APP_CONFIG_KEY_CLIENT_SECRETS])
        with safe_open(secrets_path, 'w') as fp:
            json.dump(client_secrets, fp)


def get_service_object(service, version, user, user_data=None):
    token_path = f'/tmp/ytmdl/{user}_token.json'
    secrets_path = '/tmp/ytmdl/client_secrets.json'

    store = file.Storage(token_path)

    user_data = user_data or firestore.get(const.FIRESTORE_USERS, user)
    if user_data:
        with safe_open(token_path, 'w') as fp:
            fp.write(user_data[const.FIRESTORE_USERS_KEY_TOKEN])
        creds = store.get()
    else:
        _lazy_init_clint_secrets(secrets_path)
        flow = client.flow_from_clientsecrets(secrets_path, SCOPES)
        creds = tools.run_flow(flow, store)
        with safe_open(token_path) as fp:
            token_str = fp.read()
            firestore.set(const.FIRESTORE_USERS, user, {const.FIRESTORE_USERS_KEY_TOKEN: token_str})

    return googleapiclient.discovery.build(service, version, credentials=creds)
