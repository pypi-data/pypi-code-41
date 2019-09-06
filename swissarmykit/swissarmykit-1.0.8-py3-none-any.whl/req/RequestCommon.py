import json
import sys
import time
import logging
import traceback

import brotli
import requests
from random import shuffle
from urllib.parse import urlencode

from swissarmykit.data.BSoup import BItem
from swissarmykit.db.record import BaseModel
from swissarmykit.utils.fileutils import FileUtils
from swissarmykit.utils.stringutils import StringUtils
from swissarmykit.office.excelutils import ExcelUtils

from swissarmykit.req.Headers import HeadersUtils
from swissarmykit.req.BotDetect import BotDetect
from swissarmykit.req.UserAgent import UserAgentUtils
from swissarmykit.req.PathUtils import PathUtils

try:
    from definitions_prod import *
except Exception as e:
    pass  # Surpass error. Note: Create definitions_prod.py


class RequestCommon(BotDetect, HeadersUtils, UserAgentUtils, PathUtils):
    """
    Aggregation all components.
    """

    def __init__(self):
        super().__init__()
        self.is_use_proxies = False
        self.is_disable_verify = False
        self.timeout = 0

    def set_req_timeout(self, timeout=0):
        self.timeout = timeout

    def disable_ssl(self, value=True):
        self.is_disable_verify = value

    def _exception_handler(self, proxy, exception):
        msg = str(exception)
        if 'Cannot connect to proxy.' in msg:
            print('WARN: Cannot connect to proxy from %s' % proxy.get_ip())

        if self.is_log:
            self.log.info(self.get_overview())

        if self.is_use_proxies:
            self.proxies.remove(proxy)

    def _get_content(self, res):
        if self._has_br:
            return brotli.decompress(res.content).decode()
        return res.text

    def get_payload(self, str, is_json=False):
        payload = {}
        for line in str.strip().split('\n'):
            k, v = line.split(':', 1)
            payload[k] = v.strip()

        if is_json:
            return payload
        return json.dumps(payload)

    def get(self, url, override_headers: dict = None, **params):
        '''
        Main request.

        :param url: target url
        :param params: params
        :return: html
        '''
        p = None
        try:
            kwargs = self._get_kw(url, override_headers=override_headers, **params)
            res = requests.get(url, **kwargs)
            if res.status_code >= 200 and res.status_code < 300:
                self._after_request(res, url)
                return self._get_content(res)

            raise Exception('Status code: %s' % str(res.status_code))
        except Exception as e:
            msg = str(e)
            if not self.is_disable_verify and 'bad handshake' in msg:
                return self._get_no_ssl(url, params)
            self._exception_handler(p, e)

        return ''

    def _get_no_ssl(self, url, params):
        self.log.warn('Set verify=False for requests')
        kwargs = self._get_kw(params)
        res = requests.get(url, verify=False, **kwargs)
        try:
            if res.status_code >= 200 and res.status_code < 300:
                self._after_request(res, url)
                return self._get_content(res)
        except Exception as e:
            self.log.error('Disable ssl, but handshake still fail. ' + str(e))
        return ''

    def post(self, action='', override_headers = None, payload=None, payload_json=None, json=None, return_cookies=True):  # type: (str, dict, str, dict, dict, bool) -> str
        '''

        href: https://stackoverflow.com/questions/20759981/python-trying-to-post-form-using-requests
        https://stackoverflow.com/questions/26615756/python-requests-module-sends-json-string-instead-of-x-www-form-urlencoded-param

         '''
        p = None
        try:
            if payload_json:
                payload = urlencode(payload_json)
            kwargs = self._get_kw(action, override_headers=override_headers, **{'data': payload, 'json': json})

            res = requests.post(action, **kwargs)
            if res.status_code == 200:
                self._after_request(res, action)
                if return_cookies:
                    return res.cookies
                return self._get_content(res)

            raise Exception('Status code: %s' % str(res.status_code))
        except Exception as e:
            self._exception_handler(p, e)

        return ''

    def get_overview(self):
        total = self.get_total_proxies()
        in_used = self.get_total_in_used_proxies()
        load_average = round(in_used * 100 / total)
        return 'Overview: %d/%d. Load: %d%%\n' % (in_used, total, load_average)

    def get_html(self, model, url, re_scrape=False, utf_8=False, call_process_html=None):
        if not re_scrape:
            html = model.get_html_by_url(url)
            if html:
                return html

        html = self.get(url)
        if html:
            item = model.save_url(url)
            if utf_8:
                item.save_html(StringUtils.get_valid_text_for_excel(html))
            elif call_process_html:
                item.save_html(call_process_html(url, html))
            else:
                item.save_html(html)
        return html

    def get_html_of_item(self, model=None, number_threads=None, lst_model=None, base_url='', re_scrape=False,
                         utf_8=False, call_process_html=None, limit=0,
                         sleep_time=0.5):  # type: (BaseModel, int, list, str, bool, bool, any, int, int) -> None
        ''' Used for main process when have database. '''

        lst = []
        if lst_model:
            query = lst_model  # Quite hard to understand,
        else:
            query = model.select()
            if limit:
                query.limit(limit)

        for item in query:
            if re_scrape or not item.html_id:
                lst.append(item)

        def call(item: BaseModel):
            url = base_url + item.url
            if self.is_log:
                self.log.info('Get html ' + url)

            html = self.get(url)
            time.sleep(sleep_time)

            if html:
                if utf_8:
                    item.save_html(StringUtils.get_valid_text_for_excel(html))
                elif call_process_html:
                    item.save_html(call_process_html(url, html))
                else:
                    item.save_html(html)
            else:
                print('ERROR: re-try get html')  # Purpose to signal overflow.
                if self.retry_request:
                    raise Exception('Fail to get html')  # Put back to queue
                return False
            return True

        self.thread_pool(task_lst=lst, callback=call, number_threads=number_threads)

    def get_html_of_from_url_list(self, url_lst, model, number_threads=None, base_url='', no_retry_if_have_html=False,
                                  re_scrape=False, utf_8=False, call_process_html=None,
                                  sleep_time=0.5):  # type: (list, BaseModel, int, str, bool, bool, bool, any, int) -> bool
        ''' Used for general item, to update to main item. '''
        # if no_retry_if_have_html:
        #     url_lst = self._get_list_not_exists_url(url_lst, model)

        if not url_lst:
            print('INFO: get_html_of_from_url_list(model=%s) - List is empty.' % model.get_name())
            return False

        lst = []
        if not re_scrape:
            skip = 0
            lst_exists = []
            lst_exists_item = {}

            for item in model.select(model.url, model.html_id):
                lst_exists.append(item.url)
                lst_exists_item[item.url] = item

            for url in url_lst:
                if url not in lst_exists or not lst_exists_item.get(url).html_id:
                    lst.append(url)
                else:
                    skip += 1
            print('INFO: Skip already scrape: %d' % skip)

        def call(url):
            url = base_url + url
            html = self.get(url)
            time.sleep(sleep_time)

            if html:
                item = model.save_url(url)  # type: BaseModel
                if utf_8:
                    item.save_html(StringUtils.get_valid_text_for_excel(html))
                elif call_process_html:
                    item.save_html(call_process_html(url, html))
                else:
                    item.save_html(html)
            else:
                print('ERROR: re-try get html')
                if self.retry_request:  # // todo: because disable retry, so can not count fail task
                    raise Exception('Error: Fail to get html')  # Put back to queue
                return False
            return True

        self.thread_pool(task_lst=lst, callback=call, number_threads=number_threads)
        print('INFO: Done scrape url. Total: %d\n' % model.count())

        return True

    def login(self, url, payload=None, payload_json=None, json=None, cookies_name=None, cache=False, retry=False):
        if not cache:
            return self.set_cookies(self.post(action=url, payload=payload, payload_json=payload_json, json=json, return_cookies=True))

        if not cookies_name:
            cookies_name = StringUtils.get_letter_only(url)

        file = appConfig.CONFIG_PATH + '/' + cookies_name + '.pickle'
        cookies = FileUtils.load_object_from_file(file)
        if retry or not cookies:
            cookies = self.set_cookies(self.post(action=url, payload=payload, payload_json=payload_json, json=json, return_cookies=True))
            FileUtils.dump_object_to_file(cookies, file)
        else:
            self.extra_headers.update(cookies)

        return cookies

    def _get_list_not_exists_url(self, lst, model):
        new_lst = []
        for i in lst:
            if not model.exists_url(i):
                new_lst.append(i)
        return new_lst

    def get_cookies(self, url, override_headers: dict = None, **params):
        req = requests.session()
        p = None
        try:
            kwargs = self._get_kw(url, override_headers=override_headers, **params)
            res = req.get(url, **kwargs)
            if res.status_code == 200:
                lst = []
                for key, val in res.cookies.get_dict().items():
                    lst.append(key + '=' + val)
                return '; '.join(lst)
            raise Exception('Status code: %s' % str(res.status_code))
        except Exception as e:
            self._exception_handler(p, e)

        return ''

    def get_cache(self, url, override_headers: dict = None, retry=False, **params):
        req_cache = BaseModel.get_class('requests_cache')
        req = req_cache.get_by_url(url)
        if req and not retry:
            print('INFO: Load html from cache')
            return req.get_html()
        else:
            html = self.get(url, override_headers=override_headers, **params)
            req_cache.save_url(url, html=html)
            print('INFO: Save html to cache')
            return html

    def drop_cache(self):
        req_cache = BaseModel.get_class('requests_cache')
        req_cache.truncate_table()
        print('INFO: Drop all cache')

    def print_get(self, url):
        print(self.get(url))
        print('.', end='', flush=True)

    def notify(self, msg):
        return True

    def notify_error(self, msg):
        return True

    def enable_notify(self, enable=True):
        self._enable = enable
        return True

    def thread_pool(self, task_lst=None, callback=None, number_threads=None, multiple_process=False):
        timer = self.get_timer(len(task_lst))
        for task in task_lst:
            try:
                callback(task)
                timer.check()
                print('.', end='', flush=True)
            except Exception as e:
                traceback.print_exc(file=sys.stdout)

    def is_use_one_proxy(self):
        return False

    def __str__(self):
        return '%s' % (self.get_overview())


if __name__ == '__main__':
    req = RequestCommon()
    # req.enable_debug()
    req.set_headers('''
Accept: image/webp,image/apng,image/*,*/*;q=0.8
Accept-encoding: gzip, deflate
Accept-language: en-US,en;q=0.9
Cache-control: no-cache
Pragma: no-cache
Referer: https://www.netcarshow.com/
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36
    ''')
    # print(req.get_headers())
    # req.download_image(file_name=AppConfig.get_desktop_path() + '/im3.jpg', image_url='https://readthedocs.org/sustainability/view/391/VTqqlvCa9q51/', override_headers={'Referer': 'host3'})
    # text = req.get('https://stackoverflow.com/questions/10606133/sending-user-agent-using-requests-library-in-python')
    print(req.get_cookies('https://stackoverflow.com/'))
