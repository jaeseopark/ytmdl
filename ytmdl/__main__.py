"""
This file is intended to run locally.
TODO: Create a GCP-hosted flask app that will replace this local script.
"""

import os

from ytmdl import firestore, const
from ytmdl.utils import gcp_utils
from ytmdl.utils.io_utils import safe_open


def get_token_path(service_name, service_version):
    secrets_path = '/tmp/ytmdl/client_secrets.json'
    _lazy_init_clint_secrets(secrets_path)
    return gcp_utils.authenticate(service_name, service_version, secrets_path)


def _lazy_init_clint_secrets(secrets_path):
    if not os.path.exists(secrets_path):
        config_dict_ref = firestore.find(const.FIRESTORE_APP, const.FIRESTORE_APP_CONFIG)
        config_dict = firestore.to_dict(config_dict_ref)
        client_secrets_str = config_dict[const.FIRESTORE_APP_CONFIG_KEY_CLIENT_SECRETS]
        with safe_open(secrets_path, 'w') as fp:
            fp.write(client_secrets_str)


if __name__ == "__main__":
    while True:
        service, version = input("Enter service & API version to authorize\n> ").split(",")
        token_path = get_token_path(service, version)
        print(token_path)
        input("\nHit enter to continue\n> ")
