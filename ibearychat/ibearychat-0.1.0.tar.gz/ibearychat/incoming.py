# -*- coding: utf-8 -*-
#
# @ reference:
#    https://github.com/bearyinnovative/bearychat-docs/blob/master/tutorials/markdown/incoming.md

import os
import sys
import json

import requests


class BearychatIncoming(object):
    def __init__(self, webhook_url):
        self.webhook = webhook_url
        self.headers = {"Content-Type": "application/json"}
        self.payload = {
            "text": "**This is the pretext.**",
            "attachments":[
                {
                    "title"   : "This is the title.",
                    "markdown": "true",
                    "url"     : "",
                    "color"   : "#70cc29",
                    "text"    : "This is the first line.\n This is the second line."
                }
            ]
        }

    def set_url(self, url):
        self.payload["attachments"][0]["url"] = url

    def set_payload(self, payload):
        self.set_pretext(payload["pretext"])
        self.set_title(payload["title"])
        self.set_color(payload["color"])
        self.set_text(payload["text"])

    def set_pretext(self, pretext):
        self.payload["text"] = pretext

    def set_title(self, title):
        self.payload["attachments"][0]["title"] = title
       
    def set_color(self, color):
        self.payload["attachments"][0]["color"] = color

    def set_text(self, text_list):
        self.payload["attachments"][0]["text"] = "\n".join(text_list)

    def curl(self):
        print("curl %s -X POST -d 'payload=%s'" % (self.webhook, json.dumps(self.payload)))

    def push(self):
        r = requests.post(self.webhook, data=json.dumps(self.payload), headers=self.headers)
        return r



def bearychat_incoming(webhook_url, pretext="", title="", url="", color="#70cc29", text_list=[], payload={}, debug=False):
    incoming = BearychatIncoming(webhook_url)
    if payload:
        incoming.set_payload(payload)
    else:
        incoming.set_pretext(pretext)
        incoming.set_title(title)
        incoming.set_url(url)
        incoming.set_color(color)
        incoming.set_text(text_list)

    if debug == True:
        incoming.curl()
    return incoming.push()


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

    bearychat_incoming(webhook_url, payload=payload, debug=True)

