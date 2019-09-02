# -*- coding: utf-8 -*-

from .incoming import bearychat_incoming


if __name__ == "__main__":
    webhook_url = "your_incoming_url"
    payload = {
        "pretext"   : "This is pretext.",
        "title"     : "This is title.",
        "url"       : "This is title.",
        "color"     : "#70cc29",
        "text"      : ["This is the first line.", "This is the second line"],
    }
    bearychat_incoming(
        webhook_url,
        pretext="This is pretext.",
        title="This is title.",
        url="https://www.teachmyself.cn.",
        color="#70cc29",
        text_list=["This is the first line.", "This is the second line"],
        debug=True
    )
