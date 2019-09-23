import json
import time

from dateutil import parser

import const
import firestore
from utils import oauth_utils

LIST_LIMIT = 100


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
        params = {"part": "id,snippet", "playlistId": playlist_id, "maxResults": LIST_LIMIT if LIST_LIMIT < 50 else 50}
        if token:
            params.update({"pageToken": token})

        video_req = svc.playlistItems().list(**params)
        r = video_req.execute()

        transformed_items += [transform_item(i) for i in r.get("items", list())]

        token = r.get("nextPageToken")

        if not token or len(transformed_items) >= LIST_LIMIT:
            break

    return transformed_items[:LIST_LIMIT]


def process_user(request=None):
    request_json = request.get_json(silent=True)
    user = request_json['user']

    user_data = firestore.get(const.FIRESTORE_USERS, user)
    svc_youtube = oauth_utils.get_service_object("youtube", "v3", user, user_data)
    videos = get_liked_videos(svc_youtube)

    last_processed = user_data.get(const.FIRESTORE_USERS_KEY_LAST_PROCESSED, 0)
    videos_to_process = [v for v in videos if v['liked_at'] > last_processed]

    if videos_to_process:
        # TODO: put videos_to_process on Cloud Tasks queue

        last_processed = videos[0]["liked_at"] if videos else 0
        user_data.update({const.FIRESTORE_USERS_KEY_LAST_PROCESSED: last_processed})
        firestore.set(const.FIRESTORE_USERS, user, user_data)

    return json.dumps({'videos': videos, 'videos_to_process': videos_to_process}, ensure_ascii=False)


def process_video(request=None):
    raise NotImplementedError
