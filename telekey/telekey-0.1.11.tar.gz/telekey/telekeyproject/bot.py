import logging
import sys

from telegram import ext
from app.hanlders import HANDLERS


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

updater = ext.Updater("YOUR TOKEN")

for handler in HANDLERS:
    updater.dispatcher.add_handler(handler)

if __name__ == "__main__":
    updater.start_polling()
    print('service started ...')
    updater.idle()
