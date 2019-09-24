import os
from typing import Sequence

import firebase_admin
import google as google
from firebase_admin import firestore

from utils import gcp_utils

creds = gcp_utils.get_service_creds()
if gcp_utils.is_cloud():
    firebase_admin.initialize_app(creds, {'projectId': os.getenv('GCP_PROJECT')})
else:
    firebase_admin.initialize_app(creds)

db = firestore.client()


def find(*args: Sequence, doc_ref=None):
    assert len(args) % 2 == 0
    doc_ref = (doc_ref or db).collection(args[0]).document(args[1])
    args = args[2:]
    if args:
        return find(args, doc_ref=doc_ref)
    else:
        return doc_ref


def to_dict(doc_ref):
    try:
        doc = doc_ref.get()
        return doc.to_dict()
    except google.cloud.exceptions.NotFound:
        return None
