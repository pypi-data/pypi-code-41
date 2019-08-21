"""
Slack Bot Track Command
"""

import logging
import requests
import pendulum

from ebr_trackerbot.bot import register_command
from time_utility import parse_time_delta_input


def show_command(text, result, payload, config, commands):
    """
    Slack Bot Show Command
    """

    target_test = result.group(1)
    duration = result.group(2)

    logging.debug("Show command on " + target_test + " over " + duration)

    time_now = pendulum.now("UTC")

    start = parse_time_delta_input(duration, time_now)

    response = requests.get(
        config["api_url"],
        params={"test_status": "failed", "start": start.to_iso8601_string(), "end": time_now.to_iso8601_string()},
        headers={"accept": "application/json"},
    )

    channel_id = payload["data"]["channel"]
    thread_ts = payload["data"]["ts"]

    if "tests" not in response.json():
        logging.warning("Invalid JSON from api call. Does not contains tests field.")
        payload["web_client"].chat_postMessage(
            channel=channel_id, text="Something went wrong, please report this failure.", thread_ts=thread_ts
        )
        return

    for test in response.json()["tests"]:
        full_name = test["full_name"]
        if full_name == target_test:
            count = str(test["count"])
            payload["web_client"].chat_postMessage(
                channel=channel_id,
                text="Test *{test}* failed {count} times over the last {duration}".format(
                    test=target_test, count=count, duration=duration
                ),
                thread_ts=thread_ts,
            )
            break
    else:
        payload["web_client"].chat_postMessage(
            channel=channel_id,
            text="Test *{test}* never failed over {duration}".format(test=target_test, duration=duration),
            thread_ts=thread_ts,
        )


register_command(
    "show",
    "Shows the current status of a test over the past time interval. Command syntax: show full_testname over time_interval."
    + "Time interval can contain *s* - seconds, *m* - minutes, *h* - hours, *d* - days"
    + "(eg. 20d5h10m5s)",
    "^show ([^ ]+) over ((?:[0-9]+(?:s|m|h|d))+)$",
    show_command,
)
logging.info("Show command registered")
