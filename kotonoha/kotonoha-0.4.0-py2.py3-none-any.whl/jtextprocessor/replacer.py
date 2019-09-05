# -*- coding: utf-8 -*-
# Copyright 2019 Bruno Toshio Sugano <brunotoshio@gmail.com>

import re


def replace_urls(text, replace_text=''):
    return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', replace_text, text)


def replace_numbers(text, replace_text='#'):
    return re.sub(r'[0-9０-９]+(?:\.[0-9０-９]*)?', replace_text, text)


def replace_prices(text, replace_text='#円'):
    return re.sub(r'[0-9０-９]{1,3}(?:,?[0-9０-９]{3})*(?:\.[0-9０-９]*)?円', replace_text, text)


def replace_with_regex(text, regex, replace_text=''):
    return re.sub(regex, replace_text, text)


def lower(text):
    return text.lower()
