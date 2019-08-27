import telebot
import datetime


class WPTelegramBot:
    def __init__(self, token: str, chat_ids: list):
        # apihelper.proxy = {'https': 'socks5h://400426223:o49EsVRy@orbtl.s5.opennetwork.cc:999'}
        # apihelper.proxy = {"http": "https://5.39.91.73:3128"}
        self.bot = telebot.TeleBot(token=token)
        self.chats = chat_ids
        self.current_code: str = None

    def send_message(self, message):
        for chat_id in self.chats:
            self.bot.send_message(chat_id=chat_id, text=message)

    def get_code(self) -> str:
        self.current_code = None
        now_timestamp = datetime.datetime.timestamp(datetime.datetime.now())

        @self.bot.message_handler(content_types=['text'])
        def get_text_messages(message):
            if message.date > now_timestamp and message.chat.id in self.chats:
                self.current_code = message.text
            if self.current_code is not None:
                self.bot.stop_polling()

        self.bot.polling()
        return self.current_code
