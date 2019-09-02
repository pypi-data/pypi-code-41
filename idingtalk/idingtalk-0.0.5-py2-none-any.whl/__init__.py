# -*- coding: utf-8 -*-

from .incoming import dingtalk_incoming


if __name__ == "__main__":
    token = ""
    payload = {
        "msgtype" : "markdown",
        "markdown": {
            "title": "This is the title!",
            "text" : "\n\n".join([
                "# This is title",
                "> This is first line.",
                "> This is second line.",
                ])
        },
        "at" : {
            "atMobiles": ["18600000000"],
            "isAll": False
        }
    }
    dingtalk_incoming(token, payload=payload, at_mobiles=["18600000000"])
