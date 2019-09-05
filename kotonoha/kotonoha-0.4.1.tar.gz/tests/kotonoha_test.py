#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging
from unittest import mock

from kotonoha import kotonoha


@mock.patch('kotonoha.kotonoha.alpha_to_full')
def test_class_jtext_alpha_to_full(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'alpha_to_full'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.digits_to_half')
def test_class_jtext_digits(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'digits'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.kana_to_full')
def test_class_jtext_to_full_width(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'to_full_width'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.lower')
def test_class_jtext_lower(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'lower'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_numbers')
def test_class_jtext_replace_numbers(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'replace_numbers': {'replace_text': 'n'}}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_numbers')
def test_class_jtext_remove_numbers(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'remove_numbers'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_prices')
def test_class_jtext_replace_prices(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'replace_prices': {'replace_text': '$'}}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_prices')
def test_class_jtext_remove_prices(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'remove_prices'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_urls')
def test_class_jtext_replace_url(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'replace_url': {'replace_text': 'url'}}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_urls')
def test_class_jtext_remove_url(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'remove_url'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_hashtags')
def test_class_jtext_replace_hashtag(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'replace_hashtags'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_emails')
def test_class_jtext_replace_email(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'replace_emails'}
    ])
    jtext.run('kore')
    assert mocked.called


@mock.patch('kotonoha.kotonoha.replace_mentions')
def test_class_jtext_replace_mention(mocked):
    jtext = kotonoha.Kotonoha()
    jtext.prepare([
        {'replace_mentions'}
    ])
    jtext.run('kore')
    assert mocked.called


def test_class_jtext_prepare():
    jtext = kotonoha.Kotonoha()
    list_of_tasks = [
        {'alpha_to_full'},
        {'digits'},
        {'to_full_width'},
        {'lower'},
        {'replace_numbers': {'replace_text': 'n'}},
        {'remove_numbers'},
        {'replace_prices': {'replace_text': '$'}},
        {'remove_prices'},
        {'replace_url': {'replace_text': 'url'}},
        {'remove_url'},
        {'replace_hashtags': {'replace_text': 'hash'}},
        {'replace_emails': {'replace_text': 'email'}},
        {'replace_mentions': {'replace_text': 'mention'}}
    ]
    assert len(list_of_tasks) == len(jtext._operators.keys())
    jtext.prepare(list_of_tasks)
    assert len(jtext._pipeline) == len(list_of_tasks)


def test_class_jtext_prepare_error(caplog):
    with caplog.at_level(logging.ERROR):
        jtext = kotonoha.Kotonoha()
        jtext.prepare([{'non_existing_task'}])
        assert ['Invalid operation: non_existing_task'] == [rec.message for rec in caplog.records]
