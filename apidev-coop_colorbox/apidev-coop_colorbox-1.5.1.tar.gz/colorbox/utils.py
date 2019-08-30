# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unicodedata


def assert_popup_redirects(response, url):
    """assert the colorbox response redirects to the right page"""
    if response.status_code != 200:
        raise Exception("colobox Response didn't redirect as expected: Response code was {0} (expected 200)".format(
            response.status_code)
        )

    ascii_url = unicodedata.normalize('NFKD', url).encode("utf8", 'ignore')
    expected_content = b'<script>$.colorbox.close(); window.location="' + ascii_url + b'";</script>'

    if response.content != expected_content:
        raise Exception("Don't redirect to {0}".format(url))


def assert_popup_refresh(response):
    """assert the colorbox response redirects to the right page"""
    if response.status_code != 200:
        raise Exception("colobox Response didn't redirect as expected: Response code was {0} (expected 200)".format(
            response.status_code)
        )

    expected_content = b'<script>$.colorbox.close(); window.location=window.location;</script>'

    if response.content != expected_content:
        raise Exception("Don't refresh page")
