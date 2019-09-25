import os
from typing import Sequence

import firebase_admin
import google as google
from firebase_admin import firestore
from google.cloud.firestore_v1 import CollectionReference

from ytmdl.utils import gcp_utils

creds = gcp_utils.get_service_creds()
if gcp_utils.is_cloud():
    firebase_admin.initialize_app(creds, {'projectId': os.getenv('GCP_PROJECT')})
else:
    firebase_admin.initialize_app(creds)

db = firestore.client()

_types = {
    'integerValue': int,
    'booleanValue': bool,
    'stringValue': str,
}


def find(*args: Sequence, doc_ref=None):
    doc_ref = doc_ref or db
    if isinstance(doc_ref, CollectionReference):
        doc_ref = doc_ref.document(args[0])
    else:
        doc_ref = doc_ref.collection(args[0])

    args = args[1:]
    if args:
        return find(*args, doc_ref=doc_ref)
    else:
        return doc_ref


def to_dict(doc_ref):
    try:
        doc = doc_ref.get()
        return doc.to_dict()
    except google.cloud.exceptions.NotFound:
        return None


def handle_event(firestore_event: dict):
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

    handled["id"] = firestore_event["value"]["name"].split("/")[-1]
    return handled
