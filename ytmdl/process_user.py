import json
import logging
import time

from dateutil import parser

from ytmdl import const, firestore
from ytmdl.utils import gcp_utils

LOGGER = logging.getLogger(__name__)


def get_liked_videos(svc):
    def transform_item(item):
        """
        Transforms a Youtube PlaylistItem (https://developers.google.com/youtube/v3/docs/playlistItems) into a simpler JSON object with the following fields: video_id, title, liked_at
        :param item: JSON representation of a PlaylistItem
        :return: The transformed JSON object
        """
        video_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        liked_at = int(time.mktime(parser.parse(item['snippet']['publishedAt']).utctimetuple()))
        return {"video_id": video_id, "title": title, "liked_at": liked_at}

    channel_req = svc.channels().list(part="contentDetails", mine=True)

    playlist_id = channel_req.execute()['items'][0]['contentDetails']['relatedPlaylists']['likes']

    token = None
    transformed_items = []

    while True:
        params = {"part": "id,snippet", "playlistId": playlist_id, "maxResults": const.YOUTUBE_LIST_LIMIT if const.YOUTUBE_LIST_LIMIT < 50 else 50}
        if token:
            params.update({"pageToken": token})

        video_req = svc.playlistItems().list(**params)
        r = video_req.execute()

        transformed_items += [transform_item(i) for i in r.get("items", list())]

        token = r.get("nextPageToken")

        if not token or len(transformed_items) >= const.YOUTUBE_LIST_LIMIT:
            break

    return transformed_items[:const.YOUTUBE_LIST_LIMIT]


def process_user(event, context=None):
    LOGGER.info(json.dumps(event))
    handled_event = firestore.handle_event(event)

    if const.FIRESTORE_USERS_KEY_LAST_TRIGGERED not in handled_event:
        # Not interested in other updates.
        return

    user = handled_event["id"]

    user_ref = firestore.find(const.FIRESTORE_USERS, user)
    user_data = firestore.to_dict(user_ref)
    svc_youtube = gcp_utils.get_service_object("youtube", "v3", user_data[const.FIRESTORE_USERS_KEY_YOUTUBE_TOKEN])
    videos = get_liked_videos(svc_youtube)

    last_processed = user_data.get(const.FIRESTORE_USERS_KEY_LAST_PROCESSED, 0)
    videos_to_process = [v for v in videos if v['liked_at'] > last_processed]

    if videos_to_process:
        batch = firestore.batch()
        for v in videos_to_process:
            video_document_ref = firestore.find(const.FIRESTORE_USERS_KEY_VIDEOS, v["video_id"], doc_ref=user_ref)
            batch.set(video_document_ref, v)
        batch.commit()
        last_processed = videos[0]["liked_at"] if videos else 0
        user_ref.update({const.FIRESTORE_USERS_KEY_LAST_PROCESSED: last_processed})

    response = {'videos': videos, 'videos_to_process': videos_to_process}
    LOGGER.info(json.dumps(response))
    return response
