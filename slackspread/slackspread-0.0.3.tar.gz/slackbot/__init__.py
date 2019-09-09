
from certifi import where
from datetime import datetime
from os import environ
import re
import slack
import ssl


class SlackBot:
    """Slack web client to build a python slack bot.
    
    ``Slackbot`` is a simple wrapper around basic API calls to slack API.
    Instantiation needs an environment variable storing the connexion token.
    When initiating a ``Slackbot`` instance, the bot id is read from slack API
    and stored as attribute.
    
    :param token: name for environment variable storing slack application token
    :type token: str
    
    :ivar client: the slack web client instance with which API calls are made
    :type client: ``slack.WebClient()``
    
    :cvar mention_regex: a regex to identify a direct mention in a text
    :type mention_regex: str
    :ivar id: the bot's id
    :type id: str
    """
    mention_regex = '<@(|[WU].+?)>(.*)'
    
    def __init__(self, token):
        ssl_context = ssl.create_default_context(cafile = where())
        self.client = slack.WebClient(token = environ.get(token), ssl = ssl_context)
        self.id = self.client.auth_test().data['user_id']
        
    def __repr__(self):
        return "SlackBot(id = %s)" % self.id

    def users_list(self) -> list:
        """Get the list of non-deleted users.
        
        A wrapper around ``slack.WebClient.users_list``. It returns
        a flat list of dictionaries, with keys ``name``, ``id`` and ``email``.
        ``id`` is used to tag people in messages with the syntax ``<@%s> % id``.
        """
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
    def parse_mention(message_text, regex) -> tuple:
        """From a message, find and extract a mention and the related text.
        
        Result is a length-two tuple of the form ``(user_id, text)``. If no
        mention is found in the message, the result is ``(None, text)``.
        
        :param message_text: the body of a message
        :type message_text: str
        :param regex: the regex identifying a mention. Using ``SlackBot.mention_regex``
            will usually suffice
        :type regex: regex
        """
        matches = re.search(regex, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, message_text)
    
    def send_message(self, channel, message) -> None:
        """Immediate wrap around ``slack.WebClient.chat_postMessage()``"""
        self.client.chat_postMessage(
            channel = channel,
            text = message
        )
        
    @staticmethod
    def _read_time(x: str) -> tuple:
        """Convert an hour in ``HH:mm`` string format into an integer tuple."""
        sep = ":"
        time_regex = r'([01][0-9]|2[0-3])%s[0-5][0-9]' % sep
        assert isinstance(x, str)
        assert bool(re.findall(pattern = time_regex, string = x)), "Time must be given as HH%smm" % sep
        return tuple([int(el) for el in x.split(sep)])
        
    @staticmethod
    def closing_time(closing_hour: str, rtm_client = None) -> None:
        """Close an RTM client if the current hour is later than the given closing hour.
        
        :param closing_hour: hour after which RTM client must be stopped. 
            Must be in ``HH:mm`` string format
        :type closing_hour: str
        :param rtm_client: The RTM client to stop (see above to see usage)
        :type rtm_client: ``slack.RTMClient()``
        """
        now = SlackBot._read_time(datetime.now().strftime("%H:%M"))
        closing = SlackBot._read_time(closing_hour)
        if now[0] >= closing[0] and now[1] >= closing[1]:
            try:
                rtm_client.stop()
            except AttributeError:
                pass
        return
