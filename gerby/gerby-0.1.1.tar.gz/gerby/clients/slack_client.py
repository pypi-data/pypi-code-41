from gerby.secrets import SLACK_TOKEN
from slackclient import SlackClient as S


class SlackClient(S):
    def __init__(self):
        return super().__init__(SLACK_TOKEN)
