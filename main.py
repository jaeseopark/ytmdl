import json
import time

from dateutil import parser

import const
import firestore
from utils import gcp_utils, oauth_utils

LIST_LIMIT = 100


def process_item(item):
    liked_at = int(time.mktime(parser.parse(item['snippet']['publishedAt']).utctimetuple()))
    video_id = item['snippet']['resourceId']['videoId']
    title = item['snippet']['title']
    return {"liked_at": liked_at, "video_id": video_id, "title": title}


def get_liked_videos(user: str, user_data):
    svc = oauth_utils.get_service_object("youtube", "v3", user, user_data)
    channel_req = svc.channels().list(part="contentDetails", mine=True)

    playlist_id = channel_req.execute()['items'][0]['contentDetails']['relatedPlaylists']['likes']

    token = None
    items = []

    while True:
        params = {"part": "id,snippet", "playlistId": playlist_id, "maxResults": LIST_LIMIT if LIST_LIMIT < 50 else 50}
        if token:
            params.update({"pageToken": token})

        video_req = svc.playlistItems().list(**params)
        r = video_req.execute()

        items += [process_item(i) for i in r.get("items", list())]

        token = r.get("nextPageToken")

        if not token or len(items) >= LIST_LIMIT:
            break

    return items[:LIST_LIMIT]


def process_user(request=None):
    if gcp_utils.is_cloud():
        request_json = request.get_json(silent=True)
        user = request_json['user']
    else:
        user = const.FIRESTORE_USERS_DEFAULT

    user_data = firestore.get(const.FIRESTORE_USERS, user)
    videos = get_liked_videos(user, user_data)

    last_processed = user_data.get(const.FIRESTORE_USERS_KEY_LAST_PROCESSED, 0)
    videos_to_process = [v for v in videos if v['liked_at'] > last_processed]

    if videos_to_process:
        # TODO: put videos_to_process on Cloud Tasks queue

        last_processed = videos[0]["liked_at"] if videos else 0
        user_data.update({const.FIRESTORE_USERS_KEY_LAST_PROCESSED: last_processed})
        firestore.set(const.FIRESTORE_USERS, user, user_data)

    return json.dumps({'videos': videos, 'videos_to_process': videos_to_process}, ensure_ascii=False)


if __name__ == "__main__":
    print(process_user())
