
from certifi import where
from datetime import datetime
from os import environ
import re
import slack
import ssl


class SlackBot:
    """Slack web client to build a python slack bot."""
    mention_regex = '<@(|[WU].+?)>(.*)'
    
    def __init__(self, token):
        ssl_context = ssl.create_default_context(cafile = where())
        self.client = slack.WebClient(token = environ.get(token), ssl = ssl_context)
        self.id = self.client.auth_test().data['user_id']

    def users_list(self) -> list:
        """Get flat users list with name, slack id and mail, without deleted users."""
        members = self.client.users_list().data['members']
        users = []
        for member in members:
            if not member["deleted"]:
                try:
                    users.append({
                        "name": member["real_name"],
                        "id": member["id"],
                        "email": member["profile"]["email"],
                    })
                except KeyError:
                    pass
        return users
    
    @staticmethod
    def parse_mention(message_text, regex):
        """Find a direct mention and return the user ID which was mentioned.

        If there is no direct mention, return ``None``.
        """
        matches = re.search(regex, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, message_text)
    
    def send_message(self, channel, message):
        self.client.chat_postMessage(
            channel = channel,
            text = message
        )
        
    @staticmethod
    def closing_time(closing_hour: str = '20:00', rtm_client = None):
        def read_time(x: str, sep: str):
            assert isinstance(x, str)
            return tuple([int(el) for el in x.split(sep)])
        now = read_time(datetime.now().strftime("%H:%M"), sep = ':')
        closing = read_time(closing_hour, sep = ':')
        if now[0] >= closing[0] and now[1] >= closing[1]:
            try:
                rtm_client.stop()
            except AttributeError:
                pass
