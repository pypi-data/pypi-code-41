# -*- coding: utf-8 -*-
#
# @reference:
#    https://ding-doc.dingtalk.com/doc#/serverapi2/qf2nxq    

import os
import sys
import json
import requests


class DingtalkIncoming(object):
    def __init__(self, token):
        if not token:
            print("token can not be empty!")
            sys.exit(0)
        self.token = token
        self.url   = "https://oapi.dingtalk.com/robot/send?access_token=%s" % (token)
        self.at = []
        self.headers = {"User-Agent": "DingTalkAgent", "Content-type": "application/json"}
        self.payload = {
            "msgtype" : "markdown",
            "markdown": {
                "title": "This is the title!",
                "text" : "This is the text content!"
            },
            "at" : {
                "atMobiles": ["18600000000"],
                "isAll": False
            }
        }

    def set_headers(self, headers={}):
        if headers:
            self.headers = headers

    def set_title(self, title=""):
        if title:
            self.payload["markdown"]["title"] = title

    def set_text(self, text_list=[]):
        if text_list:
            self.payload["markdown"]["text"] = "\n\n".join(text_list)

    def set_at_mobiles(self, at_mobiles=[], at_all=False):
        if at_all:
            self.payload["at"]["isAll"] = True
        else:
            if at_mobiles:
               at = "@%s "*len(at_mobiles) % tuple(at_mobiles)
               self.payload["at"]["atMobiles"] = at_mobiles
               self.payload["markdown"]["text"] = "\n\n".join([self.payload["markdown"]["text"], at])

    def set_payload(self, payload={}):
        if payload:
            self.payload = payload

    def get_payload(self):
        return self.payload

    def push(self):
        r = requests.post(self.url, data=json.dumps(self.payload), headers=self.headers)
        return r

    def curl(self):
        print("curl -X POST -H \"Content-type: application/json\" --data-binary '%s' %s" % (json.dumps(self.payload), self.url))
        

def dingtalk_incoming(token, title="", text=[], at_mobiles=[], at_all=False, payload={}, debug=False):
    incoming = DingtalkIncoming(token)
    
    if payload:
        incoming.payload = payload
        incoming.set_at_mobiles(at_mobiles=payload["at"]["atMobiles"], at_all=payload["at"]["isAll"])
    else:
        incoming.set_title(title)
        incoming.set_text(text)
        incoming.curl()
        incoming.set_at_mobiles(at_mobiles, at_all)
    
    if debug:
        print(incoming.get_payload())
        incoming.curl()
    return incoming.push()


if __name__ == "__main__":
    token = ""
    payload = {
        "msgtype" : "markdown",
        "markdown": {
            "title": "This is push title!",
            "text" : "\n\n".join([
                "# This is text title",
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
