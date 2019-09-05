#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from kotonoha import jconverter


def test_kana_to_full():
    assert jconverter.kana_to_full('これはｲｲABC1234') == 'これはイイABC1234'


def test_digits_to_half():
    assert jconverter.digits_to_half('今日は３９度みたいです1234ABC') == '今日は39度みたいです1234ABC'


def test_alpha_to_full():
    assert jconverter.alpha_to_full('takaidesu') == 'たかいです'
