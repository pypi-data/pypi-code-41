from slack import WebClient

from gerby.secrets import SLACK_TOKEN


class SlackClient(WebClient):
    def __init__(self):
        return super().__init__(SLACK_TOKEN)
