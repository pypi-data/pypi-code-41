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


def replace_hashtags(text, replace_text=''):
    return re.sub(r'(?:^|\s)#[^\s!@#$%^&*()=+./,\[{\]};:\'"?><]+', replace_text, text)


def replace_emails(text, replace_text=''):
    regex_string = r'(?:\s|^)(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"' \
        r'(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:' \
        r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])' \
        r'|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:' \
        r'(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
    return re.sub(regex_string, replace_text, text)


def replace_mentions(text, replace_text=''):
    return re.sub(r'(?:\s|^)@\w+(?=\s|$)', replace_text, text)
