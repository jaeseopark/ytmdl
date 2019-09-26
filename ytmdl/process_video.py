import json
import logging

from youtube_dl import YoutubeDL

from ytmdl import firestore
from ytmdl.utils.io_utils import makedirs_auto

LOGGER = logging.getLogger(__name__)


def download(video_id: str, path=None, ext="mp3"):
    assert isinstance(video_id, str)

    makedirs_auto("/tmp/ytmdl")
    output_template = path or "/tmp/ytmdl/%(title)s-%(id)s.%(ext)s"

    # progress = {}

    def my_hook(d):
        LOGGER.info(json.dumps(d))
        # if d['status'] == 'finished':
        #     print('Done downloading, now converting ...')

    params = {
        'nocheckcertificate': True,
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': ext,
            'preferredquality': '192',
        }],
        'progress_hooks': [my_hook],
        "logger": LOGGER
    }

    YoutubeDL(params).download(["https://www.youtube.com/watch?v=" + video_id])


def process_video(event, context=None):
    LOGGER.info(json.dumps(event))
    handled_event = firestore.handle_event(event)
    download(handled_event["id"])
    # TODO: upload to gdrive
