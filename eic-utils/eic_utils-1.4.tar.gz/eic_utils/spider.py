import requests, re
import queue, time, os
import threading
from lxml import etree
from eic_utils.colorful_str import colorful_str
from eic_utils.procedure import procedure

default_allow_patterns = ['^(http|ftp).*$'] 
default_target_patterns = ['^(http|ftp).*$']

class Spider(object):
    def __init__(self, start_urls,# {{{
                 allow_patterns=default_allow_patterns,
                 target_patterns=default_target_patterns,
                 encoding=None, thread_num=4, max_tries=4):
        """
            Args:
                start_urls: str or list of str
                allow_patterns: str, re or list of str, re
                target_patterns: str, re or list of str, re

        """

        self.cnt = 0
        self.thread_num = thread_num
        self.max_tries = max_tries
        self.encoding = encoding
        self.is_target_url = 1
        self.is_allow_url = 2
        
        with procedure('init patterns'):
            if isinstance(start_urls, str):
                start_urls = [start_urls]
            if isinstance(allow_patterns, str):
                allow_patterns = [allow_patterns]
            if isinstance(target_patterns, str):
                target_patterns = [target_patterns]
            
            self.allow_patterns = [re.compile(s) if isinstance(s, str) else s for s in allow_patterns]
            self.target_patterns = [re.compile(s) if isinstance(s, str) else s for s in target_patterns]

            self.q = queue.Queue(maxsize=0)
            self.vis = set()
            for url in start_urls:
                self.q.put([url, self.query_url(url)])
                self.vis.add(url)

        self.sess = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/76.0.3809.100 Safari/537.36',
        }
        self.sess.headers = headers

        with procedure('init workers'):
            self.working_status = 0
            self.working_status_lock = threading.Lock()
            self.threadings = [threading.Thread(target=self.crawl, args=[i])\
                    for i in range(thread_num)]
    # }}}
    def query_url(self, url):# {{{
        st = 0
        for each_pattern in self.allow_patterns:
            if each_pattern.match(url) is not None:
                st |= self.is_allow_url
                break
        for each_pattern in self.target_patterns:
            if each_pattern.match(url) is not None:
                st |= self.is_target_url
                break
        return st
    # }}}
    def run(self):# {{{
        for t in self.threadings:
            t.start()

        for t in self.threadings:
            t.join()
    # }}}
    def crawl(self, idx):# {{{
        print(colorful_str.log('thread #(#b){}(#) starts').format(idx))
        while True:
            with self.working_status_lock:
                if self.working_status == 0 and self.q.empty():
                    break
            try:
                with self.working_status_lock:
                    url, status = self.q.get(False)
                    self.working_status ^= 1 << idx
                    self.cnt += 1
            except queue.Empty:
                time.sleep(0.1)
                continue
            ##### CODE ####
            print(colorful_str.log('#(#b){}(#) gets (#y){}(#)'.format(idx, url)))
            with procedure('#(#b){}(#) done: (#g){}(#), remain: (#y){}(#)'.format(idx, self.cnt, self.q.qsize())):
                response = self.fetch_url(url)
                if response is not None:
                    results = self.run_page(response, url, status)
                    for result in results:
                        self.q.put(result)
            ##### #### ####
            with self.working_status_lock:
                self.working_status ^= 1 << idx

        print(colorful_str.log('thread #(#b){}(#) finishs').format(idx))
    # }}}
    def fetch_url(self, url):# {{{
        for i in range(self.max_tries):
            try:
                response = self.sess.get(url)
                if self.encoding is not None:
                    response.encoding = self.encoding
            except Exception as e:
                print(colorful_str.err('{}'.format(e)))
                continue
            return response
        return None
    # }}}
    def run_page(self, response, url, status):# {{{
        if (status & self.is_target_url) > 0:
            self.run_target(response, url)
        if (status & self.is_allow_url) == 0:
            return []


        xml = etree.HTML(response.text)
        urls = xml.xpath('//a/@href')
        urls = [requests.compat.urljoin(response.url, url) for url in urls]
        
        results = []
        for url in urls:
            st = self.query_url(url)
            if st > 0:
                results.append([url, st])
        return results
    # }}}
    def run_target(self, response, url):# {{{
        raise(NotImplementedError)
    # }}}

if __name__ == '__main__':
    start_urls = ['http://huaxiaozhuan.com/']
    target_patterns = '^http://huaxiaozhuan.com/.*.html$'
    spider = Spider(start_urls, encoding='utf-8', target_patterns=target_patterns)
    spider.run()

