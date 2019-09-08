""" Hawking Telegram Bot.

Telegram-bot API reference:
https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#fetch-images-sent-to-your-bot.
"""
import logging
import logging.config
import os
import sys
import random

from hawking.frontend.engine.default import engine
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


def start(update, context):
    logging.info("Conversation started!")
    update.message.reply_text('Welcome, to next gen search engine')


def help(update, context):
    logging.info("Help requested!")
    update.message.reply_text("I'm Hawking, `/ask` <anything>")


def handle_query(update, context):
    if update.message == None:
        return

    if update.message.text == None:
        return

    namespace = "chat_" + str(update.message.chat.id)
    query = update.message.text
    if query.startswith("/ask"):
        query = query[len("/ask"):]
        query = query.strip()

    logging.info('search within "%s" namespace for "%s"', namespace, query)

    if query.startswith("http"):
        entity_type = 'image'
    else:
        entity_type = 'text'
    results = engine.search(namespace, 3, query, entity_type)

    chat_id = update.message.chat.id
    if entity_type == 'image':
        # For testing
        # results = [
        #     ("https://storage.googleapis.com/imagestash001/906802_3a8ac174-a9cc-4e46-88b3-bfda75941d9f_1076_1061.png", 0),
        #     ("https://storage.googleapis.com/imagestash001/23924271_8b9fb814-228b-4d4e-b51c-3e7943cd1c43_1080_1080.jpg", 1),
        #     ("https://storage.googleapis.com/imagestash001/122138742_71ddecc0-6531-4007-a622-91b076c0b602_1208_1208.jpg", 2)
        # ]
        for result in results:
            context.bot.send_photo(chat_id, result[0])
    else:
        sticker_ids = [
            'CAADAgADYwADJxRJC5prZI7aN9pbFgQ',
            'CAADAgADaAADJxRJC5_7BxWEYU1nFgQ',
            'CAADAwADVQADCZURAAFEBwkgoXPB0BYE',
            'CAADAgADKQcAAmMr4gnhM9ccDb2hKBYE',
            'CAADAgADmAcAAmMr4gkxuVuNCmpEdhYE',
            'CAADAgAD0wgAAgi3GQLjMLXpwKu9HxYE',
            'CAADAgADaAMAAn7yxQzzQ-DbolYIjxYE',
            'CAADAwADVQADCZURAAFEBwkgoXPB0BYE',
        ]
        context.bot.send_sticker(chat_id, sticker=random.choice(sticker_ids))
        message = '*Query*: *"{}"*\n\n'.format(query)
        rank = 1
        for result in results:
            message += '  {}. "{}"\n'.format(rank, result[0])
            rank += 1
        logging.info(message)
        context.bot.send_message(chat_id, text=message, parse_mode='HTML', reply_id=None)


def ask(update, context):
    handle_query(update, context)


def image_handler(update, context):
    print('image_handler triggered ...')
    file_id = update.message.photo[-1].file_id
    chat_id = update.message.chat.id
    logging.info('Received image. chat-id: {}. file-id: {}'.format(str(chat_id), file_id))
    image_uri = '/tmp/{}{}.jpg'.format(file_id, chat_id)
    logging.info('Download image: {}'.format(image_uri))
    file = context.bot.get_file(file_id)
    print(file)
    file.download(image_uri)

    namespace = "chat_" + str(update.message.chat.id)
    results = engine.search(namespace,
                            3,
                            'file:{}'.format(image_uri)
                            , 'image')

    # For testing
    # results = [
    #     ("https://storage.googleapis.com/imagestash001/906802_3a8ac174-a9cc-4e46-88b3-bfda75941d9f_1076_1061.png", 0),
    #     ("https://storage.googleapis.com/imagestash001/23924271_8b9fb814-228b-4d4e-b51c-3e7943cd1c43_1080_1080.jpg", 1),
    #     ("https://storage.googleapis.com/imagestash001/122138742_71ddecc0-6531-4007-a622-91b076c0b602_1208_1208.jpg", 2)
    # ]
    for result in results:
        context.bot.send_photo(chat_id, result[0])


def process(update, context):
    if update.message == None:
        return

    if update.message.message_id == None:
        return

    if update.message.text == None:
        return

    embeddings = []
    if update.message.reply_to_message != None:
        if update.message.reply_to_message.text != None:
            embeddings.append(update.message.reply_to_message.text)
    embeddings.append(update.message.text)

    namespace = "chat_"+str(update.message.chat.id)
    reference = str(update.message.message_id)

    if engine.index(namespace, reference, embeddings):
        logging.info("%s/%s, %s inserted", namespace, reference, embeddings)
    else:
        logging.info("%s/%s, %s updated", namespace, reference, embeddings)


def process_entity(update, context):
    logging.info(update)


def error(update, context):
    logging.warning('"%s" error "%s"', update, context.error)


def serve(bot_token=None):
    if bot_token is None and "BOT_TOKEN" not in os.environ:
        logging.error("Environment variable BOT_TOKEN not defined, bot won't start!")
        return None

    if os.environ.get("BOT_TOKEN") is not None:
        bot_token = os.environ["BOT_TOKEN"]
    updater = Updater(bot_token, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("ask", ask))
    dp.add_handler(MessageHandler(Filters.photo, image_handler))
    dp.add_handler(MessageHandler(Filters.text, process))
    dp.add_handler(MessageHandler(Filters.sticker, process_entity))
    dp.add_error_handler(error)

    print('Started bot service ...')
    updater.start_polling()
    return updater


def main():
    updater = serve()
    if updater is not None:
        updater.idle()


if __name__ == '__main__':
    main()
