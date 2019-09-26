import json

from ytmdl.process_video import process_video


def test_process_video():
    with open('test/resource/firestore_event_video_create_new_doc.json') as fp:
        event = json.load(fp)

    process_video(event)
