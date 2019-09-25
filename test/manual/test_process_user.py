import json

import main
from ytmdl.utils.io_utils import safe_open


def test_process_user_default():
    response = main.process_user({
        "updateMask": {},
        "value": {}
    })

    try:
        # For local debugging...
        with safe_open("/tmp/ytmdl/test/test_process_user_default.json", 'w') as fp:
            json.dump(response, fp, ensure_ascii=False, indent=2)
    finally:
        pass
