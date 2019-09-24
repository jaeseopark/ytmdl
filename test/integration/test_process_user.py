import json

import const
import main
from utils.io_utils import safe_open


class MockRequest:
    # TODO: create a proper mock object using pytest module

    def __init__(self, user):
        self.user = user

    def get_json(self, **kwargs):
        return {'user': self.user}


def test_process_user_default():
    m_req = MockRequest(const.FIRESTORE_USERS_DEFAULT)
    response = main.process_user(m_req)

    # TODO: assertions

    try:
        # For local debugging...
        with safe_open("/tmp/ytmdl/test/test_process_user_default.json", 'w') as fp:
            json.dump(response, fp, ensure_ascii=False, indent=2)
    finally:
        pass
