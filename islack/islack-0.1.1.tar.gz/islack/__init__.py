# -*- coding: utf-8 -*-

from .incoming import slack_incoming

name = "islack"

slack_colors = {
    "default": "#b8daff", # blue
    "sucess" : "#2db67c", # green
    "error"  : "#D00000", # red
    "warn"   : "#ffeeba", # yellow
    "info"   : "#d6d8db", # gray
}

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
