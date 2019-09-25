import json

from ytmdl.firestore import handle_event


def test_update_existing_field():
    with open('test/resource/firestore_event_update_existing_field.json') as fp:
        event = json.load(fp)

    handled_event = handle_event(event)

    lt = handled_event["last_triggered"]
    assert lt[0] == 1569387601
    assert lt[1] == 1569389005
    assert handled_event["id"] == "default"


def test_update_new_field():
    with open('test/resource/firestore_event_update_new_field.json') as fp:
        event = json.load(fp)

    handled_event = handle_event(event)

    lt = handled_event["last_triggered"]
    assert lt[0] is None
    assert lt[1] == 1569389560
    assert handled_event["id"] == "default"
