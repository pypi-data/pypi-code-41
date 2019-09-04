import requests
import json
import logging


class VeriUsAPIGateway:

    def __init__(self, apikey):
        self.apikey = apikey
        self.headers = {'Content-Type': 'application/json', "apikey": self.apikey}
        self.function_dictionary = {
            "text-similarity": self.text_similarity,
            "language-detection": self.language,
            "abusive-content-detection": self.abusive,
            "text-summarization": self.summary,
            "keyword-extraction": self.keywords,
            "entity-extraction": self.named_entities,
            "distorted-language-detection": self.distorted,
            "intent-detection": self.intent,
            "morphological-analysis": self.morphology,
            "sexual-content-detection": self.sexual,
            "gibberish-detection": self.gibberish,
            "normalization": self.normal,
            "deasciifier": self.deasciified,
            "sentence-tokenizer": self.sentence_tokens,
            "arabic-text-summarization": self.arabic_summary,
            "arabic-keyword-extraction": self.arabic_keywords,
            "arabic-sentiment-classification": self.arabic_sentiment,
            "arabic-news-classification": self.arabic_news_class,
            "turkish-stemmer": self.stem,
            "sentiment-analysis": self.sentiment,
            "sentiment-classification": self.sentiment,
            "topic-detection": self.topics,
            "taxonomy": self.taxonomy
        }

    def __post_to_access(self, endpoint, text1, text2=None):

        if text1 and text2:
            data = {"text1": text1, "text2": text2}

        elif text1:
            data = {"text": text1}
        else:
            result = {"result": None, "confidency": None, "message": "Please enter a text."}
            return result

        try:
            response = requests.post("https://api.verius.ai/" + endpoint,
                                     headers=self.headers, data=json.dumps(data).encode('utf-8'))
            result = response.json()
        except Exception as e:
            logging.warning(e)
            result = {"result": None, "confidency": None, "message": "Can not reach Verius API"}

        return result

    def text_similarity(self, text1, text2):
        return self.__post_to_access(endpoint="text-similarity", text1=text1, text2=text2)

    def semantic_similarity(self, text1, text2):
        return self.__post_to_access(endpoint="semantic-similarity", text1=text1, text2=text2)

    def language(self, text):
        return self.__post_to_access(endpoint="language-detection", text1=text)

    def abusive(self, text):
        return self.__post_to_access(endpoint="abusive-content-detection/abusive-content-detection", text1=text)

    def summary(self, text):
        return self.__post_to_access(endpoint="text-summarizer", text1=text)

    def keywords(self, text):
        return self.__post_to_access(endpoint="keyword-extractor", text1=text)

    def named_entities(self, text):
        return self.__post_to_access(endpoint="entity-extraction", text1=text)

    def distorted(self, text):
        return self.__post_to_access(endpoint="distorted-language-detection", text1=text)

    def intent(self, text):
        return self.__post_to_access(endpoint="intent-detection", text1=text)

    def product_category(self, text):
        return self.__post_to_access(endpoint="product-category-classification", text1=text)

    def morphology(self, text):
        return self.__post_to_access(endpoint="morphology", text1=text)

    def sexual(self, text):
        return self.__post_to_access(endpoint="sexual-content-detection", text1=text)

    def gibberish(self, text):
        return self.__post_to_access(endpoint="gibberish-detection", text1=text)

    def normal(self, text):
        return self.__post_to_access(endpoint="normalization/normalization", text1=text)

    def deasciified(self, text):
        return self.__post_to_access(endpoint="deasciifier/deasciifier", text1=text)

    def sentence_tokens(self, text):
        return self.__post_to_access(endpoint="sentence-tokenizer", text1=text)

    def sentiment(self, text):
        return self.__post_to_access(endpoint="sentiment-analysis/sentiment-analysis", text1=text)

    def arabic_sentiment(self, text):
        return self.__post_to_access(endpoint="arabic-sentiment-analysis", text1=text)

    def arabic_news_class(self, text):
        return self.__post_to_access(endpoint="arabic-news-classification", text1=text)

    def stem(self, text):
        return self.__post_to_access(endpoint="stemmer", text1=text)

    def arabic_summary(self, text):
        return self.__post_to_access(endpoint="arabic-text-summarizer", text1=text)

    def topics(self, text):
        return self.__post_to_access(endpoint="topic-detection", text1=text)

    def arabic_keywords(self, text):
        return self.__post_to_access(endpoint="arabic-keyword-extractor", text1=text)

    def taxonomy(self, text):
        return self.__post_to_access(endpoint="taxonomy_web", text1=text)
