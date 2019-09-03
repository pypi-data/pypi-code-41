import hashlib
import os
import re
import shutil
import geoip2.database

import requests
import urllib3

from core.rule_db import (
    session,
    Rule,
    init_db
)
import tarfile
import sys
from urllib.parse import urljoin


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Scan():

    def __init__(self, url, whether_get_address=False, user_agent=None):
        self.url = url
        self.user_agent = user_agent
        self.result = {}
        self.assets = {}
        self.path = os.path.join(os.getcwd(), 'dbs', 'GeoLite2-City.mmdb')
        self.req_obj = requests.get(url=url, headers={"User-Agent": user_agent}, verify=False, stream=True)
        if not os.path.exists(os.path.join(os.getcwd(), 'dbs', 'rule.db')):
            init_db()  # 初始化本地数据库
        if whether_get_address:
            if not os.path.exists(self.path):
                self.__download_and_tar_geolite()
                self._get_address()
            else:
                self._get_address()


    def __download_and_tar_geolite(self, url='https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'):
        req = requests.get(url=url, stream=True, verify=False, headers={"User-Agent": self.user_agent})
        if req.status_code == 200:
            total_size = int(req.headers['Content-Length'])
            if total_size > 0:
                if os.path.exists(os.path.join(os.getcwd(), 'dbs', 'GeoLite2-City.tar.gz')):
                    temp_size = os.path.getsize(os.path.join(os.getcwd(), 'dbs', 'GeoLite2-City.tar.gz'))
                else:
                    temp_size = 0
                headers = {"User-Agent": self.user_agent, 'Range': 'bytes=%d-' % temp_size}
                re_req = requests.get(url, stream=True, verify=False, headers=headers)
                with open(os.path.join(os.getcwd(), 'dbs', 'GeoLite2-City.tar.gz'), 'ab') as f:
                    for chuck in re_req.iter_content(chunk_size=1024):
                        if chuck:
                            temp_size += len(chuck)
                            f.write(chuck)
                            f.flush()
                            done = int(50 * temp_size / total_size)
                            sys.stdout.write(
                                "正在进行数据库下载(不要结束程序)：[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                            sys.stdout.flush()
                        print()  # 避免上面\r 回车符
                if temp_size == total_size:
                    try:
                        file = tarfile.open(os.path.join(os.getcwd(), 'dbs', 'GeoLite2-City.tar.gz'))
                        file.extractall(path=os.path.join(os.getcwd(), 'dbs'))
                        walk = os.listdir(os.path.join(os.getcwd(), 'dbs'))
                        for i in walk:
                            if 'GeoLite2-City_' in i:
                                src_path = os.path.join(os.getcwd(), 'dbs', i, 'GeoLite2-City.mmdb')
                                des_path = os.path.join(os.getcwd(), 'dbs')
                                shutil.move(src_path, des_path)
                                break
                        file.close()
                        return True
                    except:
                        raise FileNotFoundError('文件解压失败')

            else:
                raise ConnectionError('无法定位数据库位置')
        else:
            raise ConnectionError('无法连接数据库')

    def _check_url(self):
        if self.req_obj.status_code >400:
            return False
        else:
            return True
    def _match_web_server(self):
        headers = self.req_obj.headers
        web_server = headers.get('server')
        if web_server:
            self.assets['web_server'] = [web_server]

    def _get_title(self):
        title = re.search(r'<title>(.*?)</title>|<TITLE>(.*?)</TITLE>', self.req_obj.text.replace(' ','').replace('\n',''), re.I).groups()[0]
        if title:
            self.result['Title'] = title

    def _get_rule(self):
        rules = session.query(Rule).all()
        return rules

    def _get_ip(self):
        source_obj = self.req_obj.raw._connection.sock
        if source_obj:
            source = source_obj.getpeername()
            ip = source[0] or ''
            port = source[1] or ''
            self.result['Remote Address'] = '{}:{}'.format(ip, port)
        else:
            ip = None
        return ip

    def _get_address(self):
        ip = self._get_ip()
        if ip:
            Ip_Address = {}
            reader = geoip2.database.Reader(self.path)
            response = reader.city(ip)
            Ip_Address['Country'] = response.country.name
            Ip_Address['Province'] = response.subdivisions.most_specific.name
            Ip_Address['City'] = response.city.name
            Ip_Address['Longitude And Latitude'] = 'Longitude:{}，Latitude：{}'.format(response.location.longitude,
                                                                                     response.location.latitude)
            if Ip_Address:
                self.result['Location'] = Ip_Address


    def _match_re(self, text, regex):
        return re.compile(regex.split('\\;')[0], flags=re.IGNORECASE).search(text)


    def _match_md5(self, content):
        m = hashlib.md5()
        m.update(content)
        psw = m.hexdigest()
        return psw

    def _match_dict(self, d1, d2):
        for k2, v2 in d2.items():
            v1 = d1.get(k2)
            if v1:
                if not self._match_re(v1, v2):
                    return False
            else:
                return False
        return True

    def _get_categories(self, app):
        app_obj = session.query(Rule).filter_by(rule_name=app).first()
        return app_obj


    def _add_result(self, app_name):
        if app_name:
            # print(app_name)
            if '-' in app_name:
                app = app_name.split('-')[0]
            else:
                app = app_name
            rule = session.query(Rule).filter_by(rule_name=app_name).first()
            # print(obj.category.category_name)
            if rule:
                cat = rule.category.category_name
                if cat not in self.assets.keys():
                    self.assets[cat] = []
                if app not in self.assets[cat]:
                    self.assets[cat].append(app)
                implies = rule.rule_des
                if implies != 'None':
                    if not isinstance(implies, list):
                        implies = [implies]
                    for app in implies:
                        self._add_result(app)

    def _scan(self):
        self.req_obj.encoding = self.req_obj.apparent_encoding
        for rule in self._get_rule():
            if rule.rule_method == 'url内容':
                if self._match_re(self.url, rule.rule_pattern):
                    print('url', rule.rule_name)
                    self._add_result(rule.rule_name)

            elif rule.rule_method == 'header特征':   #用于检测用户输入URL，返回响应头信息匹配
                if  'Nginx' in rule.rule_name :
                    print(rule.rule_name, rule.rule_pattern,self.req_obj.headers)
                if self._match_dict(self.req_obj.headers, eval(rule.rule_pattern)):
                    print('头',rule.rule_name)
                    self._add_result(rule.rule_name)

            elif rule.rule_method == '首页特征':   #用于检测用户输入url的Html检测
                if rule.rule_undefined == 'meta':  #用于检测meta标签
                    metas = dict(re.compile('<meta[^>]*?name=[\'"]([^>]*?)[\'"][^>]*?content=[\'"]([^>]*?)[\'"][^>]*?>', re.IGNORECASE).findall(self.req_obj.text))
                    for name, content in eval(rule.rule_pattern).items():
                        for name in metas:
                            if self._match_re(metas[name], content):
                                print('meta', rule.rule_name)
                                self._add_result(rule.rule_name)
                                break

                patterns = rule.rule_pattern
                if  patterns.startswith('[') and patterns.endswith(']'):
                    patterns = eval(patterns)
                else:
                    patterns = [patterns]
                # print(patterns)
                for pattern in patterns:
                    if self._match_re(self.req_obj.text, pattern):
                        print('内容', rule.rule_name)
                        self._add_result(rule.rule_name)

            elif rule.rule_method == 'url md5匹配':    #适用于图片链接，获取MD5值
                url_join = rule.rule_join_url
                if url_join:
                    req = requests.get(urljoin(self.url, url_join), headers={"User-Agent": self.user_agent})
                    bytes = req.content
                else:
                    bytes = self.req_obj.content
                md5 = rule.rule_pattern
                if md5:
                    if md5 == self._match_md5(bytes):
                        self._add_result(rule.rule_name)

            elif rule.rule_method == '404页面特征':   #用户寻找404页面特征,规则中给出404链接
                url_join = rule.rule_join_url
                if url_join:
                    req = requests.get(urljoin(self.url, url_join), headers={"User-Agent": self.user_agent})
                    if req.status_code == 404:
                        text = req.text
                        if self._match_re(text, rule.rule_pattern):
                            self._add_result(rule.rule_name)

            elif rule.rule_method == 'url状态码':    #匹配指定url的状态码,规则中给出状态码
                url_join = rule.rule_join_url
                if url_join:
                    req = requests.get(urljoin(self.url, url_join), headers={"User-Agent": self.user_agent})
                    status_code = rule.rule_pattern
                    if req.status_code == int(status_code):
                        self._add_result(rule.rule_name)
            else:
                pass

    def run(self):
        if self._check_url():
            self._scan()
            self._get_title()
            self.result['Header'] = self.req_obj.headers
            if 'web_server' not in self.assets:
                self._match_web_server()
            self.result['Assets'] = self.assets
        else:
            print('URL无法访问！')
        return self.result


if __name__ == '__main__':
    a = Scan(url='https://www.baidu.com/')
    a.run()

