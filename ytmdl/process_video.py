import json
import logging

from ytmdl import firestore

LOGGER = logging.getLogger(__name__)


def process_video(event, context=None):
    LOGGER.info(json.dumps(event))  # removeme
    handled_event = firestore.handle_event(event)
    LOGGER.info(json.dumps(handled_event))  # removeme
