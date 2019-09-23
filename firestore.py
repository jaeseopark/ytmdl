import os

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


def get(collection_id: str, document_id: str):
    doc_ref = db.collection(collection_id).document(document_id)
    try:
        doc = doc_ref.get()
        return doc.to_dict()
    except google.cloud.exceptions.NotFound:
        return None


def set(collection_id: str, document_id: str, data: dict):
    db.collection(collection_id).document(document_id).set(data)
