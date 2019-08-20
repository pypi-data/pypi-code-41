# -*- coding: utf-8 -*-
# @Time     : 2019/8/18 15:01
# @Author   : Run
# @File     : m3u8.py
# @Software : PyCharm

"""
1. 每轮内对于单个片段爬取失败后都会立即重新尝试retry次，一轮结束后如果仍有爬取失败片段，会对失败片段再来一轮，直至全部爬取成功。
2. 实现AES解密。
3. 通过ffmpeg合并ts视频片段为mp4格式文件，速度较慢，且合并出来的视频比网页上原视频长了2min，但视频播放效果很好。
4. 速度测试
【网速】
上传速度：3.55 MB/秒（上传带宽：28.37 Mb)
下载速度：5.53 MB/秒（下载带宽：44.28 Mb)
预估您的宽带为44.28 Mb
【结果】下载1.61G耗用239.07s
"""

from utils import *
from random import randint
from Crypto.Cipher import AES
from gevent import monkey; monkey.patch_all()
from gevent.pool import Pool
import gevent
from urllib.parse import urljoin
import os
import time
from tqdm import tqdm


def check_ffmpeg_installed():
    """
    检查windows系统下是否已经安装了ffmpeg，并将其添加至了环境变量
    :return: bool
    """
    test = os.popen("ffmpeg -version")
    if 'ffmpeg version' in test.read():
        print('ffmpeg installed')
        return True
    else:
        print('please install ffmpeg and add it to environment virables')
        return False


class M3U8Spider:
    """
    crawl HLS(HTTP Live Streaming)
        1. request m3u8 file by m3u8 url
        2. parse ts splits url and key(might not exists)
        3. download ts splits
        4. decrypt by key if encrypted
        5. concat to mp4 file
    """
    def __init__(self, output='movies/', pool_size=50, retry=3):
        """

        :param output: 下载视频存放路径
        :param pool_size:
        :param retry:
        """
        self.pool = Pool(pool_size)
        self.retry = retry
        self.session = get_http_session(pool_size, pool_size, retry)
        #
        self.ts_urls = None  # [ts_url, ...]
        self.index_url_list = None  # [(index, ts_url), ...]
        self.key = None  # if not None, bytes of length 16
        self.num = 0  # number of ts splits
        self.succeed = 0  # store succeed num to update processing bar
        self.failed_list = []
        self.file_name = None  # used to name mp4 file and ts splits's folder
        self.ts_folder = None
        #
        self.root_dir = os.getcwd()  # record root dir, initial working directory
        output = output.strip('\\')
        if not output.endswith('/'):
            output = output + '/'
        self.output_folder = output
        if not os.path.exists(output):
            os.mkdir(output)

    def reset(self):
        self.ts_urls = None  # [ts_url, ...]
        self.index_url_list = None  # [(index, ts_url), ...]
        self.key = None  # if not None, bytes of length 16
        self.num = 0  # number of ts splits
        self.succeed = 0  # store succeed num to update processing bar
        self.failed_list = []
        self.file_name = None  # used to name mp4 file and ts splits's folder
        self.ts_folder = None

    def get_ts_urls_and_key(self, m3u8_url, timeout=10):
        """

        :param m3u8_url: url of detailed m3u8 file
        :return: bool
        """
        # get m3u8
        try:
            req = self.session.get(m3u8_url, timeout=timeout)
            if req.status_code != 200:
                print('failed crawl m3u8: {}'.format(m3u8_url))
                return False
            body = req.text
        except:
            print('failed crawl m3u8: {}'.format(m3u8_url))
            return False
        # parse m3u8
        ts_urls = []
        for line in body.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and line.endswith('.ts'):
                ts_urls.append(urljoin(m3u8_url, line))
        if len(ts_urls) == 0:
            print("m3u8 doesn't contain any ts. m3u8: {}".format(m3u8_url))
            return False
        self.ts_urls = ts_urls
        self.num = len(ts_urls)
        self.index_url_list = list(enumerate(self.ts_urls))
        print('{}\n{} splits'.format(self.file_name, self.num))
        # get key
        if '#EXT-X-KEY' in body:
            key_url = urljoin(m3u8_url, 'key.key')
            try:
                req = self.session.get(key_url, timeout=timeout)
                if req.status_code != 200:
                    print('failed crawl key: {}'.format(key_url))
                    return False
                self.key = req.content
            except:
                print('failed crawl key: {}'.format(key_url))
                return False

        return True

    def add_ts_urls_and_key(self, ts_urls, key=None):
        self.ts_urls = ts_urls
        self.num = len(ts_urls)
        self.index_url_list = list(enumerate(self.ts_urls))
        self.key = key
        print('{}\n{} splits'.format(self.file_name, self.num))

    def download_all_ts(self):
        if len(self.ts_urls) == 0:
            print("no ts url to crawl")
            return
        if self.ts_folder is None:
            if self.file_name is None:
                print("file_name is None, can't name folder to store ts splits")
                return 
            self.ts_folder = os.path.join(self.output_folder, self.file_name + '/')
            if not os.path.exists(self.ts_folder):
                os.mkdir(self.ts_folder)
        #
        self.pool.map(self._download_single_ts, self.index_url_list)
        if self.failed_list:
            self.index_url_list = self.failed_list
            self.failed_list = []
            self.download_all_ts()

    def _download_single_ts(self, index_url):
        ind, ts_url = index_url
        try:
            r = self.session.get(ts_url, timeout=30)  # 似乎有可能在timeout时间内获得不全所有数据，但r.ok显示True todo
            if r.ok:  # 似乎有可能r.ok显示True且r.status_code显示200，但事实上content未获取全，导致解密时内容的长度不是16的倍数
                cont = r.content
                # decryption
                if self.key:
                    cryptor = AES.new(self.key, AES.MODE_CBC, self.key)
                    cont = cryptor.decrypt(cont)
                # save to ts file
                with open(os.path.join(self.ts_folder, '{}.ts'.format(ind)), 'wb') as f:
                    f.write(cont)
                self.succeed += 1
            else:
                self.failed_list.append(index_url)
        except:
            self.failed_list.append(index_url)

    def _update_bar(self):
        """
        todo  1. download speed  2. 如何不让进度条重复打印
        :return:
        """
        t1 = time.time()
        bar = tqdm(total=self.num)
        num0 = 0
        while num0 < self.num:
            num = self.succeed
            if num > num0:
                bar.update(num - num0)
                num0 = num
            else:
                time.sleep(1)
        bar.close()
        print("download cost time: {}s".format(round(time.time() - t1, 2)))

    def post_process(self, concat=True, delete=True):
        t1 = time.time()
        # 使用 ffmpeg concat分离器时，如果文件名有奇怪的字符，要在file.txt中转义。方便起见，我们通过修改工作路径来实现。
        cont = '\n'.join(['file {}.ts'.format(i) for i in range(self.num)])
        with open(os.path.join(self.ts_folder, 'file.txt'), 'w') as file:
            file.write(cont)
        if concat:
            if not check_ffmpeg_installed():
                return
            os.chdir(self.ts_folder)
            file_name = os.path.join('../{}.mp4'.format(self.file_name))
            cmd = 'ffmpeg -f concat -safe 0 -i file.txt -c copy "{}" -loglevel quiet'.format(file_name)
            # print(cmd)
            print("ffmpeg started")
            os.system(cmd)
            os.chdir(self.root_dir)
            if delete:
                delete_file(self.ts_folder)
        print("post process cost {}s".format(round(time.time() - t1, 2)))

    def download_movie(self, m3u8_url, file_name="unknown", concat=True, delete=True):
        t1 = time.time()
        self.file_name = file_name + '_' + str(randint(0, 1000000))  # avoid duplicates
        if self.get_ts_urls_and_key(m3u8_url):
            g1 = gevent.spawn(self._update_bar)
            self.download_all_ts()
            g1.join()
            self.post_process(concat=concat, delete=delete)
        print("total cost time: {}s\n".format(round(time.time() - t1, 2)))

    def download_movies(self, url_name_list):
        """

        :param url_name_list: [(m3u8_url, file_name), ...]
        :return:
        """
        for m3u8_url, file_name in url_name_list:
            self.download_movie(m3u8_url, file_name)
            self.reset()


if __name__ == '__main__':
    obj = M3U8Spider(output="F:\电影")
    url_name_list = [
        (
            "http://videony.rhsj520.com:8091/0717/MVSD-365/1500kb/hls/index.m3u8",
            "淫荡的M女恶魔天使 神谷充希 - 604"
        )
    ]
    obj.download_movies(url_name_list)

