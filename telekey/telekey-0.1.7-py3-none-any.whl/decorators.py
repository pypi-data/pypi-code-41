import json

from pprint import pprint
from functools import wraps

from telegram import ChatAction


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(bot, update, *args, **kwargs):
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)

            return func(bot, update, *args, **kwargs)

        return command_func

    return decorator


def debug(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        print(update)
        return func(bot, update, *args, **kwargs)

    return wrapped


send_typing_action = send_action(ChatAction.TYPING)
send_upload_video_action = send_action(ChatAction.UPLOAD_VIDEO)
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)
