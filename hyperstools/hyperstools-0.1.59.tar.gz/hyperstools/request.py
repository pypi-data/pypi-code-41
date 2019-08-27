import logging
from traceback import format_exc

import requests


logger = logging.getLogger("requests")


class External(object):
    """
    请求外部api用的类
    """

    headers = {}

    @classmethod
    def get(cls, url, **kwargs):
        return cls.request("get", url, **kwargs)

    @classmethod
    def post(cls, url, **kwargs):
        return cls.request("post", url, **kwargs)

    @classmethod
    def request(cls, method, url, **kwargs):
        # kwargs.update(verify=False)  # 不校验ssl证书
        kwargs.update(headers=cls.headers)
        for _ in range(3):
            try:
                response = result = getattr(requests, method)(url, **kwargs)
            except requests.exceptions.Timeout:
                cls.errorLogger(method, url, reason='Timeout')
                continue
            except requests.exceptions.RequestException:
                cls.errorLogger(method, url, **kwargs)
                return {}
            else:
                break
        else:
            return {}

        try:
            result = result.json()
        except Exception as e:
            cls.errorLogger(method, url, response=response, **kwargs)
            return {}
        if result is None or result == b"":
            result = {}  # 对产品返回为'null'做处理
        cls.successLogger(method, url, response, **kwargs)
        return result

    @staticmethod
    def successLogger(method, url, response, **kwargs):
        logger.info(f"{'Request done':-^70}")
        logger.info(f"{method.upper()} {url}")
        logger.info(f"kwargs: {kwargs}")
        logger.info(f"Response: {response.text}")
        logger.info(f"{'-' * 70}\n\n\n")

    @staticmethod
    def errorLogger(method, url, reason=None, response=None, **kwargs):
        logger.info("Request:")
        logger.info(f"{method.upper()} {url}")
        logger.info(f"kwargs: {kwargs}")
        if reason is not None:
            logger.error(f"error reason: {reason}")
        if response is not None:
            resp = (
                response.content
                if not isinstance(response, (list, dict, str))
                else repr(response)
            )
            logger.error(f"Response: {resp}")
            logger.error(f"Json error: {format_exc()}")
        else:
            logger.error(f"Request error: {format_exc()}")



