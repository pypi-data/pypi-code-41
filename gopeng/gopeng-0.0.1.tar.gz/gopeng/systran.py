
import requests

from gopeng.abc import RapidAPIRequest

class Systran(RapidAPIRequest):
    def __init__(self,
                 host="systran-systran-platform-for-language-processing-v1.p.rapidapi.com",
                 key="f17416b4acmshd2335508b0e4a22p1c79e8jsnbf4792d96cfa"):
        super().__init__(host, key)
        self.endpoints = {'lemmatize': "nlp/morphology/extract/lemma",
                          'pos': "nlp/morphology/extract/pos",
                          'langid': "nlp/lid/detectLanguage/document",
                          'ner_extract': "nlp/ner/extract/entities",
                          'ner_annotate': "nlp/ner/extract/annotations",
                          'tokenize': "nlp/segmentation/segmentAndTokenize"}
        self.urls = {k:"https://" + self.host + '/' + v for k,v in self.endpoints.items()}
        pass


    def nlp_call(self, method, text, lang=None):
        query = {"input":text,"lang":lang} if lang else {"input":text}
        response = requests.get(self.urls[method],
                                headers=self.headers,
                                params=query)
        return response.json()

    def lemmatize(self, text, lang):
        return self.nlp_call('lemmatize', text, lang)

    def langid(self, text):
        return self.nlp_call('langid', text)

    def ner(self, text, lang):
        return self.nlp_call('ner_annotate', text, lang)

    def pos(self, text, lang):
        output = self.nlp_call('pos', text, lang)
        return [(token['text'], token['pos']) for token in output['partsOfSpeech']]

    def pos_tag(self, tokenized_text, lang):
        output = self.nlp_call('pos',  ' '.join(tokenized_text), lang)
        return [(token['text'], token['pos']) for token in output['partsOfSpeech']]

    def word_tokenize(self, text, lang):
        output = self.nlp_call('tokenize', text, lang)
        return [token['source'] for sent in output['segments'] for token in sent['tokens']
                if token['type'] != 'separator']

    def sent_tokenize(self, text, lang):
        output = self.nlp_call('tokenize', text, lang)
        return [sent['source'] for sent in output['segments']]

    def doc_tokenize(self, text, lang):
        output = self.nlp_call('tokenize', text, lang)
        return [[token['source'] for token in sent['tokens'] if token['type'] != 'separator']
                for sent in output['segments']]
