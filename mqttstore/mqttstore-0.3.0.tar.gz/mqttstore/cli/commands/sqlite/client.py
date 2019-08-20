# system modules
import logging
from functools import reduce, partial
import datetime
import collections
import itertools
import operator
import re

# internal modules

# external modules
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MQTTClient(mqtt.Client):
    @property
    def subscribed_topics_when_connected(self):
        return getattr(self, "_subscribed_topics_when_connected", ("#",))

    @subscribed_topics_when_connected.setter
    def subscribed_topics_when_connected(self, topics):
        self._subscribed_topics_when_connected = topics

    @property
    def parse_topic_regexes(self):
        return getattr(self, "_parse_topic_regexes", (re.compile(r"^.*$"),))

    @parse_topic_regexes.setter
    def parse_topic_regexes(self, value):
        self._parse_topic_regexes = value

    @property
    def parse_message_regexes(self):
        return getattr(self, "_parse_message_regexes", (re.compile(r"^.*$"),))

    @parse_message_regexes.setter
    def parse_message_regexes(self, value):
        self._parse_message_regexes = value

    @property
    def replacements(self):
        return getattr(self, "_replacements", tuple())

    @replacements.setter
    def replacements(self, value):
        self._replacements = value

    @property
    def store_instruction_templates(self):
        return getattr(self, "_store_instruction_templates", tuple())

    @store_instruction_templates.setter
    def store_instruction_templates(self, value):
        self._store_instruction_templates = value

    @property
    def queue(self):
        try:
            return self._queue
        except AttributeError:
            self._queue = collections.deque()
        return self._queue

    @queue.setter
    def queue(self, value):
        self._queue = value

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(
                "Client {client._client_id} now connected to "
                "{client._host}:{client._port}".format(client=self)
            )
            logger.info(
                "Subscribing client {client._client_id} on "
                "{client._host}:{client._port} to topics "
                "{topics}".format(
                    client=self,
                    topics=", ".join(
                        map(repr, self.subscribed_topics_when_connected)
                    ),
                )
            )
            self.subscribe(
                list(
                    map(
                        lambda x: (x, 0), self.subscribed_topics_when_connected
                    )
                )
            )
        else:
            logger.error(
                "Client {client._client_id} couldn't connect to "
                "{client._host}:{client._port}: result code {rc}".format(
                    rc=rc, client=self
                )
            )

    def on_disconnect(self, client, userdata, flags):
        logger.info(
            "Client {client._client_id} now disconnected from "
            "{client._host}:{client._port}".format(client=self)
        )

    def on_subscribe(self, client, obj, mid, granted_qos):
        logger.info(
            "Client {client._client_id} on "
            "{client._host}:{client._port} now subscribed "
            "to topics {topics} ".format(
                client=self,
                topics=", ".join(
                    map(repr, self.subscribed_topics_when_connected)
                ),
            )
        )

    @staticmethod
    def fmtfill(s, **info):
        """
        Fill a :any:`str.format` expression and if a key was not given, return
        ``None``
        """
        try:
            return s.format(**info)
        except KeyError as e:
            logger.debug(
                "Skipping pattern {} "
                "due to missing parse information {} in {}".format(
                    repr(s), repr(next(iter(e.args), "???")), info
                )
            )
            return None

    @classmethod
    def fmt2regex(cls, s, **info):
        """
        format a given string with :any:`fmtfill` and turn it into a regular
        expression and return ``None`` if anything didn't work.
        """
        pattern = cls.fmtfill(s, **{k: re.escape(v) for k, v in info.items()})
        if not pattern:
            return None
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            logger.warning(
                "Formatting pattern {raw} "
                " with parsed information {parsed} yields an invalid "
                " regular expression {pat}: {error}".format(
                    raw=s, parsed=info, error=e, pat=repr(pattern)
                )
            )
            return None
        return regex

    @staticmethod
    def str2num(s):
        try:
            i = int(s)
        except ValueError:
            i = None
        try:
            f = float(s)
        except ValueError:
            f = None
        return s if i == f is None else (i if i == f else f)

    def store_instructions(self, **info):
        for templates in self.store_instruction_templates:
            for table_template, insertion_templates in templates.items():
                try:
                    instruction = {
                        table_template.format(**info): {
                            column: self.str2num(value)
                            for column, value in map(
                                partial(
                                    map,
                                    operator.methodcaller("format", **info),
                                ),
                                insertion_templates,
                            )
                        }
                    }
                except KeyError as e:
                    logger.debug(
                        "Skipping store templates {templates}"
                        " due to missing key {key}".format(
                            templates=templates, key=repr(next(iter(e.args)))
                        )
                    )
                    continue
                except BaseException as e:
                    logger.error(
                        "Could not format storage "
                        "command templates {templates}: "
                        "{etype}: {error}".format(
                            templates=templates,
                            etype=type(e).__name__,
                            error=e,
                        )
                    )
                    continue
                yield instruction

    def on_message(self, client, obj, msg):
        logger.info(
            "Client {client._client_id} on "
            "{client._host}:{client._port} recieved message in topic "
            "{msg.topic}: {msg.payload}".format(client=self, msg=msg)
        )
        time_recieved = datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc
        )
        topic, message = msg.topic, msg.payload.decode(errors="ignore")
        parsedict = reduce(  # merge all named captured groups
            lambda x, y: {**x, **y},
            map(  # drop unmatched groups
                lambda d: dict(filter(lambda i: i[1] is not None, d.items())),
                map(  # extract the named captured groups
                    operator.methodcaller("groupdict"),
                    filter(  # only consider successful matches
                        bool,
                        map(  # do the match
                            lambda sr: sr[1].search(sr[0]),
                            # iterate over both message and topic parsing
                            # regexes. With the topic being parsed last, groups
                            # matched there will override same-name groups
                            # matched in the message
                            itertools.chain(
                                itertools.zip_longest(
                                    tuple(),
                                    self.parse_message_regexes,
                                    fillvalue=message,
                                ),
                                itertools.zip_longest(
                                    tuple(),
                                    self.parse_topic_regexes,
                                    fillvalue=topic,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            {},  # return an empty dict when there are no matches
        )
        logger.debug(
            "information parsed from topic "
            "{topic} and message {message}: {parsed}".format(
                topic=repr(topic), message=repr(message), parsed=parsedict
            )
        )

        parsedict_escaped = {k: re.escape(v) for k, v in parsedict.items()}
        for repl_dict in self.replacements:
            match_template, replace_template = (
                repl_dict["pattern"],
                repl_dict["replacement"],
            )
            try:
                match_pattern = match_template.format(**parsedict_escaped)
                replace_pattern = replace_template.format(**parsedict_escaped)
            except KeyError as e:
                logger.debug(
                    "Skipping replacement/match template {template}"
                    " due to missing key {key}".format(
                        template=repl_dict, key=repr(next(iter(e.args)))
                    )
                )
                continue
            except BaseException as e:
                logger.error(
                    "Could not format replacement/match pattern {pattern}: "
                    "{etype}: {error}".format(
                        pattern=repr(match_pattern),
                        etype=type(e).__name__,
                        error=e,
                    )
                )
                continue
            parsedict_update = {}
            for key, value in parsedict.items():
                try:
                    new_value, n_replacements = re.subn(
                        string=value,
                        pattern=match_pattern,
                        repl=replace_pattern,
                        flags=re.IGNORECASE,
                    )
                except BaseException as e:
                    logger.error(
                        "Could not apply replacement "
                        "{pattern} --> {replacement} on {key} value {value}: "
                        "{etype}: {error}".format(
                            pattern=repr(match_pattern),
                            replacement=repr(replace_pattern),
                            key=repr(key),
                            value=repr(value),
                            etype=type(e).__name__,
                            error=e,
                        )
                    )
                    continue
                if not n_replacements:
                    continue
                new_key = repl_dict.get("new_key")
                if not new_key:
                    new_key = key
                if new_key in parsedict or new_key in parsedict_update:
                    logger.debug(
                        "Replacing {key} value "
                        "{value} with {new_value}".format(
                            key=repr(new_key),
                            value=repr(value),
                            new_value=repr(new_value),
                        )
                    )
                else:
                    logger.debug(
                        "Adding new key {key} with value {new_value}".format(
                            key=repr(new_key), new_value=repr(new_value)
                        )
                    )
                parsedict_update[new_key] = new_value
            parsedict.update(parsedict_update)
        store_instruction = next(self.store_instructions(**parsedict), None)
        if not store_instruction:
            logger.error(
                "No appropriate storage instruction for "
                "message {msg} in topic {topic}".format(
                    msg=repr(message), topic=repr(topic)
                )
            )
            return
        logger.debug(
            "Queueing storage instruction {}".format(store_instruction)
        )
        self.queue.add(store_instruction, time_recieved)
