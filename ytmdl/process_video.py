import json
import logging
import os

from googleapiclient.http import MediaFileUpload
from youtube_dl import YoutubeDL

from ytmdl import firestore, const
from ytmdl.utils import gcp_utils
from ytmdl.utils.io_utils import makedirs_auto

LOGGER = logging.getLogger(__name__)

logging.getLogger("googleapiclient").setLevel(logging.CRITICAL)


def to_url(video_id):
    return "https://www.youtube.com/watch?v=" + video_id


def download(url: str, path=None, ext="m4a"):
    makedirs_auto(const.TMP_PATH)
    output_template = path or os.path.join(const.TMP_PATH, "%(title)s-%(id)s.%(ext)s")

    result = dict()

    def progress_log_hook(d):
        if d["status"] == "finished":
            result.update(d)

    # Construct base params
    params = {
        'nocheckcertificate': True,
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': ext,
            'preferredquality': '192',
        }]
    }

    # Log params before adding unserializable values
    LOGGER.info(json.dumps(params))

    # Add unserializable values
    params.update({
        'progress_hooks': [progress_log_hook],
        "logger": LOGGER
    })

    YoutubeDL(params).download([url])

    # Return the path of the audio file
    return "{}.{}".format(os.path.splitext(result["filename"])[0], ext)


def process_video(event, context=None):
    LOGGER.info(json.dumps(event))

    handled_event = firestore.handle_event(event)
    user = handled_event["name"].split("/")[-3]
    url = to_url(handled_event["id"])
    path = download(url)

    # Upload to Google Drive
    user_data = firestore.to_dict(firestore.find(const.FIRESTORE_USERS, user))
    service = gcp_utils.get_service_object("drive", "v3", token=user_data[const.FIRESTORE_USERS_KEY_DRIVE_TOKEN])
    key = upload(path, service, folder_id=user_data[const.FIRESTORE_USERS_KEY_DRIVE_FOLDER_ID])

    # post comment?
    # service.comments().create(fileId=key, body={'content': url}, fields='id').execute()


def upload(path, service, folder_id):
    metadata = {"name": os.path.split(path)[-1], "parents": [folder_id]}
    response = service.files().create(body=metadata, media_body=MediaFileUpload(path), fields='id').execute()
    return response["id"]
