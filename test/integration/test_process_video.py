import json

from ytmdl import firestore, process_video


def test_download_video_and_convert_to_audio():
    with open('test/resource/firestore_event_create_new_doc.json') as fp:
        event = json.load(fp)

    handled_event = firestore.handle_event(event)

    process_video.download(handled_event["id"])
