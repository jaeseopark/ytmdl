from ytmdl import const, firestore
from ytmdl.utils.time_utils import get_posix_now


def iterate_users(event=None, context=None):
    """
    Iterates through all users in Firestore and updates the 'last_triggered' field.
    Doing so will raise Firestore data events, which will subsequently trigger another function.
    :param event: PubSub event (passed in, but unused)
    :param context: Cloud Functions context (passed in, but unused)
    :return:
    """
    user_stream = firestore.find(const.FIRESTORE_USERS).stream()
    for user in user_stream:
        user.reference.update({const.FIRESTORE_USERS_KEY_LAST_TRIGGERED: get_posix_now()})
