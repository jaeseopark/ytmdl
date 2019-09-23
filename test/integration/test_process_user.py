import const
import main


class MockRequest:
    # TODO: create a proper mock object using pytest module
    
    def __init__(self, user):
        self.user = user

    def get_json(self, **kwargs):
        return {'user': self.user}


def test_process_user_default():
    m_req = MockRequest(const.FIRESTORE_USERS_DEFAULT)
    main.process_user(m_req)
