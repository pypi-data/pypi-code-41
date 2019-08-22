# -*- coding: utf-8 -*-

class UrlPreprocessor:
    """
    定义预处理器结构
    """

    def __init__(self,xspider):
        self.entryUrls=xspider["body"]["entry"]["entryUrls"]
        self.params=xspider["body"]["entry"]["params"]
        self.incrementParm=xspider["body"]["config"]["incrementParm"]
        pass

    def systemprocess(self):
        """
        解析系统参数
        :return:url
        """
        pass

    def preprocess(self):
        """
        子处理器扩展
        :return:
        """
        pass

    def incrprocess(self,params):
        """
        增量时处理传递过来的参数，根据xspider的config.incrementParam
        PAGE：获取前几页
        DATE：获取近几日
        GENERAL：获取近几条
        :return:
        """
        pass

    def process(self):
        """
        定义处理过程
        :return:
        """
        self.incrprocess()
        self.systemprocess()
        self.process()
        pass


class GeneralUrlPreprocessor(UrlPreprocessor):
    def incrprocess(self):
        """
        对不同预处理器增量逻辑可能不同
        :return:
        """
        pass

    def preprocess(self):
        pass
