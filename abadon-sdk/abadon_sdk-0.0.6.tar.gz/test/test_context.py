from abadon_lib.api.context.v0_0_1 import abadon_context


def test_check_msg():
    right_msg = {
        "content": "hhhh",
        "status": -1,
        "id": 1,
    }

    error_msg = right_msg.copy()
    error_msg["aldsfjaldfjasfd"] = ""
    error_msgs = [
        {"hhh": 1},
        error_msg
    ]

    right_msg = {
        "content": "hhhh",
        "status": -1,
        "id": 1,
    }

    for error_msg in error_msgs:
        assert not abadon_context.check_msg(error_msg)
    assert abadon_context.check_msg(right_msg)
