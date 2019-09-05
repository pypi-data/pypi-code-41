# -*- coding: utf-8 -*-
# Copyright 2019 Bruno Toshio Sugano <brunotoshio@gmail.com>

import logging

from .jconverter import alpha_to_full
from .jconverter import digits_to_half
from .jconverter import kana_to_full
from .replacer import lower
from .replacer import replace_numbers
from .replacer import replace_prices
from .replacer import replace_urls


class JTextProcessor:

    def __init__(self):
        self._pipeline = []
        self._operators = {
            'remove_url': replace_urls,
            'replace_url': replace_urls,
            'remove_prices': replace_prices,
            'replace_prices': replace_prices,
            'remove_numbers': replace_numbers,
            'replace_numbers': replace_numbers,
            'to_full_width': kana_to_full,
            'digits': digits_to_half,
            'alpha_to_full': alpha_to_full,
            'lower': lower
        }

    def prepare(self, pipeline):
        self._pipeline = []
        for step in pipeline:
            task = {}
            operation = next(iter(step))
            if operation in self._operators:
                task['handler'] = self._operators[operation]
                if isinstance(step, dict):
                    task['args'] = step[operation]
                self._pipeline.append(task)
            else:
                logging.error(f'Invalid operation: {operation}')
                return

    def run(self, text):
        next_input = text
        for task in self._pipeline:
            if 'args' in task:
                args = task['args']
                next_input = task['handler'](next_input, **args)
            else:
                next_input = task['handler'](next_input)
        return next_input
