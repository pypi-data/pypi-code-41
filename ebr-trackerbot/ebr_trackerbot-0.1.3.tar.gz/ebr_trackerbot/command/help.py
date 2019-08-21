"""
Slack Bot Help Command
"""
import logging
from ebr_trackerbot import __version__ as version
from ebr_trackerbot.bot import register_command


def help_command(text, result, payload, config, commands):
    """
    Slack Bot Help Command
    """
    logging.debug("Command help")
    user = payload["data"]["user"]
    supported_commands = ""
    for command in commands:
        supported_commands += "*" + command["command"] + "* " + command["description"] + "\n"
    response = payload["web_client"].chat_postMessage(
        channel=payload["data"]["channel"],
        text="Hi <@"
        + user
        + ">!\nI'm EBR-Trackerbot v{version}\nSupported commands:\n".format(version=version)
        + supported_commands,
        thread_ts=payload["data"]["ts"],
    )
    if "ok" not in response:
        logging.warning(response)


register_command("help", "Display this help", "^help$", help_command)
logging.info("Help command registered")
