# -*- coding: utf-8 -*-

import json
import requests


class SlackIncoming(object):
    def __init__(self):
        self.incoming_url = "YOUR_INCOMING_URL"
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.payload = {
            "channel": "#everyone",
            "username": "iSlackIncoming",
            "icon_url": "https://ca.slack-edge.com/TJ2D8P5T8-USLACKBOT-sv41d8cd98f0-72",
            "attachments": [
                {
                    "fallback": "[<https://slack.com|slack>] slack incoming!",
                    "pretext": "[<https://slack.com|slack>] slack incoming!",
                    "color": "#2db67c",
                    "fields": [
                        {
                            "title": "This is the title",
                            "value": "The content below is the value:\n cant be seprateed by \"\\n\"",
                            "short":  "false"
                        }
                    ]
                }
            ]
        }

    def set_incoming_url(self, incoming_url):
        self.incoming_url = incoming_url

    def set_headers(self, headers):
        self.headers = headers

    def set_channel(self, channel=""):
        if channel != "":
            self.payload["channel"] = channel

    def set_username(self, username):
        if username != "":
            self.payload["username"] = username

    def set_icon_url(self, icon_url=""):
        if icon_url != "":
            self.payload["icon_url"] = icon_url
  
    def set_pretext(self, pretext):
        if pretext != "":
            self.payload["attachments"][0]["fallback"] = pretext 
            self.payload["attachments"][0]["pretext"] = pretext 

    def set_color(self, color=""):
        if color != "":       
            self.payload["attachments"][0]["color"] = color

    def set_title(self, title):
        if title != "":       
            self.payload["attachments"][0]["fields"][0]["title"] = title

    def set_value(self, value=""):
        if value != "":       
            self.payload["attachments"][0]["fields"][0]["value"] = value 

    def set_short(self, short="false"):
        if short != "":       
            self.payload["attachments"][0]["fields"][0]["short"] = short

    def set_payload(self, payload={}):
        if payload:
            self.payload = payload

    def get_payload(self):
        return self.payload


    def curl(self):
        return "curl -X POST --data-urlencode 'payload=%s' %s" % (json.dumps(self.payload), self.incoming_url)

    def push(self, incoming_url):
        self.set_incoming_url(incoming_url)
        r = requests.post(self.incoming_url, data=json.dumps(self.payload), headers=self.headers)
        if not r.ok:
            print(self.get_payload())
            print(self.curl())
            print(r.content)
        return r


def slack_incoming(incoming_url, channel="", username="", icon_url="", pretext="", color="", title="", value="", payload={}, debug=False):
    incoming = SlackIncoming()

    if payload:
        incoming.set_payload(payload)
    else:
        incoming.set_channel(channel)
        incoming.set_username(username)
        incoming.set_icon_url(icon_url)
        incoming.set_pretext(pretext)
        incoming.set_color(color)
        incoming.set_title(title)
        incoming.set_value(value)
    incoming.set_incoming_url(incoming_url)

    if debug:
        print(incoming.payload)
        incoming.curl()
    return incoming.push(incoming_url)


if __name__ == "__main__":
   slack_incoming_url = ""
   print(slack_incoming(
        slack_incoming_url,
        channel="#temp",
        username="iSlackRobot",
        icon_url="https://s3-us-west-2.amazonaws.com/slack-files2/bot_icons/2019-08-12/723294116148_48.png",
        pretext="This pretest content is a [<https://slack.com|slack>] incoming test!",
        color="#cd0000",
        title="This is *title*!",
        value="This is _first_ line.\n This is _second_ line."
    ))
