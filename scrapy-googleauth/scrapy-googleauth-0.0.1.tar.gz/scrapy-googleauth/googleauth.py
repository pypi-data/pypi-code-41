from scrapy import signals
from oauth2client.service_account import ServiceAccountCredentials

class GoogleAuthDownloaderMiddleware(object):

    def __init__(self, settings):
        self.scopes = settings['GOOGLE_AUTH_SCOPES']
        self.credentials = settings['GOOGLE_AUTH_CREDENTIAL_PATH']

    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler.settings)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials, self.scopes)

        credentials.get_access_token()

        credentials.apply(request.headers)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)