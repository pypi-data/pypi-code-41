from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

class GenericPortalNewsCrawler:
    def __init__(self):
        self.session = Session()
        # self.session.mount('http://', )

    # -----------------------------
    @staticmethod
    def get_all_daily_articles(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def get_daily_articles_by_category(*args, **kwargs):
        """
        해당일자의 분야별 전체 기사 목록을 긁어옵니다
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def get_daily_main_articles(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def get_daily_most_read_articles(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def get_daily_most_commented_articles(*args, **kwargs):
        raise NotImplementedError

    # -----------------------------
    @staticmethod
    def get_article_content(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def get_article_reactions(*args, **kwargs):
        raise NotImplementedError

    def get_comment_metadata(self, *args, **kwargs):
        raise NotImplementedError

    # -----------------------------
    def get_all_comments(self, *args, **kwargs):
        raise NotImplementedError

    def get_all_replies(self, *args, **kwargs):
        raise NotImplementedError

