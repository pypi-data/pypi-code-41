#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import pytest

from kotonoha.mecab_handler import MeCabHandler


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class MecabNode:
    def __init__(self, feature):
        self.feature = feature
        self.surface = 'aaa'
        self.next = None


@pytest.fixture
def mecab_mocker():
    def mock_parse(text):
        return text

    def mock_parse_node(text):
        nodes = [
            '形容詞,,,,,,bla',
            '動詞,自立,,,,,bla',
            '動詞,,,,,,bla',
            '名詞,サ変接続,,,,,bla',
            '名詞,数,,,,,bla',
            '名詞,接尾,,,,,bla',
        ]
        initial = None
        for node in nodes:
            temp = MecabNode(node)
            temp.next = initial
            initial = temp
        return initial

    mocker = {}
    mocker['parse'] = mock_parse
    mocker['parseToNode'] = mock_parse_node
    return Struct(**mocker)


def test_basic(mecab_mocker, mocker):
    handler = MeCabHandler(mecab_mocker)
    mocker.spy(mecab_mocker, 'parse')
    mocker.spy(mecab_mocker, 'parseToNode')
    handler.basic('aaa')
    assert mecab_mocker.parse.call_count == 1
    assert mecab_mocker.parseToNode.call_count == 1


def test_meaningful(mecab_mocker, mocker):
    handler = MeCabHandler(mecab_mocker)
    mocker.spy(mecab_mocker, 'parse')
    mocker.spy(mecab_mocker, 'parseToNode')
    handler.meaningful('aaa')
    assert mecab_mocker.parse.call_count == 1
    assert mecab_mocker.parseToNode.call_count == 1


def test_by_filter(mecab_mocker, mocker):
    handler = MeCabHandler(mecab_mocker)
    mocker.spy(mecab_mocker, 'parse')
    mocker.spy(mecab_mocker, 'parseToNode')
    filter_func = mocker.stub()
    handler.by_filter('aaa', filter_func)
    assert mecab_mocker.parse.call_count == 1
    assert mecab_mocker.parseToNode.call_count == 1
    assert filter_func.call_count == 6
    assert all([a == b for a, b in zip(filter_func.call_args_list[5][0][0], ['形容詞', '', '', '', '', '', 'bla', 'aaa'])])


def test_nouns(mecab_mocker, mocker):
    handler = MeCabHandler(mecab_mocker)
    mocker.spy(mecab_mocker, 'parse')
    mocker.spy(mecab_mocker, 'parseToNode')
    handler.nouns('aaa')
    assert mecab_mocker.parse.call_count == 1
    assert mecab_mocker.parseToNode.call_count == 1


def test_verbs(mecab_mocker, mocker):
    handler = MeCabHandler(mecab_mocker)
    mocker.spy(mecab_mocker, 'parse')
    mocker.spy(mecab_mocker, 'parseToNode')
    handler.verbs('aaa')
    assert mecab_mocker.parse.call_count == 1
    assert mecab_mocker.parseToNode.call_count == 1
