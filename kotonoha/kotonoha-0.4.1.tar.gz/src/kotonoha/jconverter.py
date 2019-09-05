# -*- coding: utf-8 -*-
# Copyright 2019 Bruno Toshio Sugano <brunotoshio@gmail.com>

import jaconv


def kana_to_full(text):
    return jaconv.h2z(text, ascii=False, digit=False)


def digits_to_half(text):
    return jaconv.z2h(text, digit=True, kana=False)


def alpha_to_full(text):
    return jaconv.alphabet2kana(text)
