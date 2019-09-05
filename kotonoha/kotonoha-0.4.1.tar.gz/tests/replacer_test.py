#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from kotonoha import replacer


def test_replace_urls_with_a_text_without_url():
    text = 'This text does not contain any url'
    assert replacer.replace_urls(text) == text


def test_replace_urls_with_a_text_that_contains_an_url():
    text = 'This text contains an url http://abcd.com https://abcd.com'
    assert replacer.replace_urls(text) == 'This text contains an url  '


def test_replace_urls_with_a_different_string():
    text = 'This text contains an url http://abcd.com https://abcd.com'
    assert replacer.replace_urls(text, 'ok') == 'This text contains an url ok ok'


def test_replace_numbers_with_a_text_without_any_number():
    text = 'This text does not contain any number'
    assert replacer.replace_numbers(text) == text


def test_replace_numbers_with_a_text_that_contains_numbers():
    text = 'This text contains numbers 1234 ９２ 0.2 1,000'
    assert replacer.replace_numbers(text) == 'This text contains numbers # # # #,#'


def test_replace_numbers_with_a_different_string():
    text = 'This text contains numbers 1234 ９２ 0.2 1,000'
    assert replacer.replace_numbers(text, 'ok') == 'This text contains numbers ok ok ok ok,ok'


def test_replace_prices_with_a_text_without_any_price():
    text = 'This text does not contain any price 1234'
    assert replacer.replace_prices(text) == text


def test_replace_prices_with_a_text_that_contains_price():
    text = 'This text contains numbers 1234円 ９２円 0.2円 1,000円 ０.２円'
    assert replacer.replace_prices(text) == 'This text contains numbers #円 #円 #円 #円 #円'


def test_replace_prices_with_a_different_string():
    text = 'This text contains numbers 1234円 ９２円 0.2円 1,000円 ０.２円'
    assert replacer.replace_prices(text, 'ok') == 'This text contains numbers ok ok ok ok ok'


def test_replace_with_regex():
    text = 'This number 1234 must be changed'
    my_regular_expression = r'\d+'
    assert replacer.replace_with_regex(text, my_regular_expression) == 'This number  must be changed'


def test_replace_with_regex_and_a_different_string():
    text = 'This number 1234 must be changed'
    my_regular_expression = r'\d+'
    assert replacer.replace_with_regex(text, my_regular_expression, 'ok') == 'This number ok must be changed'


def test_lower():
    text = 'This number 1234 is SO small'
    assert replacer.lower(text) == 'this number 1234 is so small'


def test_replace_hashtags_with_a_text_without_any_hashtag():
    text = 'This text does not contain any hashtag'
    assert replacer.replace_hashtags(text) == text


def test_replace_hashtags_with_a_text_that_contains_hashtags():
    text = 'This text contains hashtags #abc a#aaa #これは'
    assert replacer.replace_hashtags(text) == 'This text contains hashtags a#aaa'


def test_replace_emails_with_a_text_without_any_email():
    text = 'This text does not contain any email'
    assert replacer.replace_emails(text) == text


def test_replace_emails_with_a_text_that_contains_emails():
    text = 'This text contains emails test.test@email.com aa@aa@aa.com aa_as.aa+asd@e.b.c.s'
    assert replacer.replace_emails(text) == 'This text contains emails aa@aa@aa.com'


def test_replace_mentions_with_a_text_without_any_mention():
    text = 'This text does not contain any mention'
    assert replacer.replace_mentions(text) == text


def test_replace_mentions_with_a_text_that_contains_mentions():
    text = 'This text contains mentions @abc @as_aa @as213_asd2 @aa.aa'
    assert replacer.replace_mentions(text) == 'This text contains mentions @aa.aa'
