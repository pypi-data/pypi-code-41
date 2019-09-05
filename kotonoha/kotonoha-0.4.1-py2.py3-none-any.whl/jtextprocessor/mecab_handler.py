# -*- coding: utf-8 -*-
# Copyright 2019 Bruno Toshio Sugano <brunotoshio@gmail.com>


class MeCabHandler:

    def __init__(self, tagger):
        self._handler = tagger

    def basic(self, text):
        self._handler.parse("")
        result = self._handler.parseToNode(text)
        filtered_words = []
        while result:
            features = result.feature.split(',')
            if features[0] == u"名詞":
                filtered_words.append(result.surface)
            else:
                filtered_words.append(features[6])
            result = result.next

        return " ".join(filtered_words)

    def meaningful(self, text):
        self._handler.parse("")
        result = self._handler.parseToNode(text)
        filtered_words = []
        while result:
            features = result.feature.split(',')
            if features[0] in {"形容詞"}:
                filtered_words.append(features[6])
            if features[0] in {"動詞"} and features[1] == "自立":
                filtered_words.append(features[6])
            if features[0] in {"名詞"} and features[1] not in {"数", "接尾"}:
                filtered_words.append(result.surface)
            result = result.next

        return " ".join(filtered_words)

    def nouns(self, text):
        self._handler.parse("")
        result = self._handler.parseToNode(text)
        filtered_words = []
        while result:
            features = result.feature.split(',')
            if features[0] in {"名詞"}:
                filtered_words.append(result.surface)
            result = result.next

        return " ".join(filtered_words)

    def verbs(self, text):
        self._handler.parse("")
        result = self._handler.parseToNode(text)
        filtered_words = []
        while result:
            features = result.feature.split(',')
            if features[0] in {"動詞"} and features[1] == "自立":
                filtered_words.append(features[6])
            if features[0] in {"名詞"} and features[1] in {"サ変接続"}:
                filtered_words.append(result.surface)
            result = result.next

        return " ".join(filtered_words)
