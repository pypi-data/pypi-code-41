from copy import deepcopy

import telegram
from telegram import KeyboardButton, InlineKeyboardButton, ReplyKeyboardRemove


def build_menu(buttons, n_cols, header_buttons=[], footer_buttons=[]):
    return header_buttons + [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)] + footer_buttons


class Page:

    def __init__(self, text, botton_list=[], header_buttons=[], footer_buttons=[], n_cols=2):
        self.text = text
        self.botton_list = botton_list
        self.header_buttons = header_buttons
        self.footer_buttons = footer_buttons
        self.n_cols = n_cols

    def markup(self, context={}):

        full_list = self.botton_list + self.header_buttons + self.footer_buttons

        botton_list = deepcopy(self.botton_list)
        for i, item in enumerate(botton_list):
            botton_list[i].text = item.text.format(**context)

        menu = build_menu(botton_list, self.n_cols, self.header_buttons, self.footer_buttons)

        if full_list == []:
            return None

        if all([isinstance(i, KeyboardButton) for i in full_list]):
            return telegram.ReplyKeyboardMarkup(menu)
        elif all([isinstance(i, InlineKeyboardButton) for i in full_list]):
            return telegram.InlineKeyboardMarkup(menu)
        else:
            raise ValueError('there is more than one types of buttons!')

    def text_remove_keyboard(self, context={}):
        return {
            'text': self.text.format(**context),
            'reply_markup': ReplyKeyboardRemove()
        }

    def caption_remove_keyboard(self, context={}):
        return {
            'caption': self.text.format(**context),
            'reply_markup': ReplyKeyboardRemove()
        }

    def text_markup(self, context={}):
        return {
            'text': self.text.format(**context),
            'reply_markup': self.markup(context)
        }

    def caption_markup(self, context={}):
        return {
            'caption': self.text.format(**context),
            'reply_markup': self.markup(context)
        }
