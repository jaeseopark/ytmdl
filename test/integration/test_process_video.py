import json
import os

from ytmdl import firestore, process_video, const


def test_download_video_and_convert_to_audio():
    with open('test/resource/firestore_event_video_create_new_doc.json') as fp:
        event = json.load(fp)

    handled_event = firestore.handle_event(event)

    path = os.path.join(const.TMP_PATH, "test_download_video_and_convert_to_audio.m4a")
    returned_path = process_video.download(process_video.to_url(handled_event["id"]), path)

    assert path == returned_path
