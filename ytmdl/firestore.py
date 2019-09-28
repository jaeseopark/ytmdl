import json
import logging
import os
from typing import Sequence

import firebase_admin
import google as google
from firebase_admin import firestore
from google.cloud.firestore_v1 import CollectionReference

from ytmdl.utils import gcp_utils

LOGGER = logging.getLogger(__name__)


class FirestoreClient:
    """
    Singleton class to store the Google Firestore client. The init logic is encapsulated in this structure because
    having the init logic in the global scope causes unit tests to fail.
    """
    __instance = None

    def __init__(self):
        def lazy_init():
            creds = gcp_utils.get_service_creds()
            if gcp_utils.is_cloud():
                # If runtime is Cloud Functions, then specify the project id.
                firebase_admin.initialize_app(creds, {'projectId': os.getenv('GCP_PROJECT')})
            else:
                # service_creds.json is required for all other environments and the file already contains the project id.
                firebase_admin.initialize_app(creds)

            return firestore.client()

        if not FirestoreClient.__instance:
            FirestoreClient.__instance = lazy_init()

    @property
    def instance(self):
        return FirestoreClient.__instance


_types = {
    'integerValue': int,
    'booleanValue': bool,
    'stringValue': str,
}


def batch():
    return FirestoreClient().instance.batch()


def _find(doc_ref, *args):
    if isinstance(doc_ref, CollectionReference):
        doc_ref = doc_ref.document(args[0])
    else:
        doc_ref = doc_ref.collection(args[0])

    args = args[1:]
    if args:
        return _find(doc_ref, *args)
    else:
        return doc_ref


def find(*args):
    """
    Given an arbitrary number of string arguments, returns the Firestore reference object.
    :param args: string values
    :return: A Firestore reference object that corresponds to the given 'args'
    """
    return _find(FirestoreClient().instance, *args)


def to_dict(doc_ref):
    try:
        doc = doc_ref.get()
        return doc.to_dict()
    except google.cloud.exceptions.NotFound:
        return None


def handle_event(firestore_event: dict):
    """
    Converts the raw Firestore event into the following format:
    {
      "field1": [old_value, new_value],
      "field2": [old_value, new_value],
      ...
    }
    :param firestore_event: Original Firestore event
    :return: The converted event
    """

    def sanitize(field_value_dict):
        if field_value_dict is None:
            return None
        typ, value = field_value_dict.popitem()
        return _types[typ](value)

    field_paths = firestore_event["updateMask"].get("fieldPaths") or list()
    handled = {k: [
        sanitize(firestore_event["oldValue"]["fields"].get(k)),
        sanitize(firestore_event["value"]["fields"].get(k))
    ] for k in field_paths}

    handled["name"] = firestore_event["value"]["name"]
    handled["id"] = firestore_event["value"]["name"].split("/")[-1]

    LOGGER.info(json.dumps(handled))

    return handled
