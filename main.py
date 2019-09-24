import json
import time
from copy import deepcopy

from dateutil import parser

import const
import firestore
from utils import oauth_utils


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


def process_user(request=None):
    request_json = request.get_json(silent=True)
    user = request_json['user']

    user_ref = firestore.find(const.FIRESTORE_USERS, user)
    user_data = firestore.to_dict(user_ref)
    org_user_data = deepcopy(user_data)
    svc_youtube = oauth_utils.get_service_object("youtube", "v3", user, user_ref=user_ref, user_data=user_data)
    videos = get_liked_videos(svc_youtube)

    last_processed = user_data.get(const.FIRESTORE_USERS_KEY_LAST_PROCESSED, 0)
    videos_to_process = [v for v in videos if v['liked_at'] > last_processed]

    if videos_to_process:
        # batch = firestore.db.batch()
        # for v in videos_to_process:
        #     video_document_ref = user_ref.collection(const.FIRESTORE_USERS_KEY_VIDEOS).document(v['video_id'])
        #     batch.set(video_document_ref, v)
        # batch.commit()
        last_processed = videos[0]["liked_at"] if videos else 0
        user_data.update({const.FIRESTORE_USERS_KEY_LAST_PROCESSED: last_processed})
        user_ref.set(user_data)

    return {'videos': videos, 'videos_to_process': videos_to_process, 'org_user_data': org_user_data, 'user_data': user_data}


def process_video(request=None):
    raise NotImplementedError
