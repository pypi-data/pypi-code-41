# -*- coding: utf-8 -*-
import base64
import random
import socket
import re
import urllib
import urllib2
import urlparse
import cx_Oracle
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
import time
from elasticsearch import Elasticsearch

from univider.esutil import save_yuqing_article,save_qtt_content,save_qtt_comment
from univider.logger import Logger
from univider.settings import es_host
from pyquery import PyQuery as pyq



class Fetcher():

    logger = Logger(__name__).getlogger()
    def persist(self,params,result):

        try:
            from univider.settings import landing
            if(landing):
                from univider.subprocessor import Subprocessor
                subprocessor = Subprocessor(landing,params,result)
                subprocessor.persist()
            else:
                pass
        except Exception,e:
            print Exception,params["user"] + ":",e

    def fetch_page_with_cache(self,params,oreader):
        if(params.has_key("iscache") and params["iscache"] == "false"):
            iscache = False
        else:
            iscache = True

        if(iscache):
            params_c = params.copy()
            del params_c['uuid']
            from univider.encrypter import get_md5_value
            ckey = get_md5_value(str(params_c))
            try:
                from univider.cacher import Cacher
                cacher = Cacher()
                cvalue = cacher.get(ckey)
                if(cvalue!= None and cvalue!=''):
                    self.logger.info('got cache ' + params['url'])
                    result = eval(cvalue)
                    # self.persist(params,result)
                    return result
            except Exception,e:
                print Exception,params["user"] + ":",e
        result = self.fetch_page(params,oreader)
        if(iscache):
            try:
                cacher.set(ckey,str(result))
                self.logger.info(params["user"] + 'cached source ' + params['url'])
            except Exception,e:
                print Exception,params["user"] + ":",e
        self.persist(params,result)
        return result

    def fetch_page(self,params,oreader):
        date=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        uuid = params["uuid"]
        node = socket.gethostname()

        try:
            url = params["url"]
            if(params.has_key("headers")):
                headers = urlparse.parse_qs(params["headers"], False)
            else:
                headers = {}

            if(params.has_key("method") and params["method"] == "POST"):
                # POST
                if(params.has_key("post.params")):
                    data = params["post.params"]
                else:
                    data = None
                req = urllib2.Request(url=url, data=data, headers=headers)
            else:
                # GET
                if url.startswith("http://mp.weixin.qq.com") or url.startswith("https://mp.weixin.qq.com"):
                    url = url.replace(u"%3D","=",10)
                    if "chksm" in url:
                        url = url[:url.index("&chksm")]
                    es = Elasticsearch(es_host)
                    index = "yuqing_index"
                    doc_type = "article"
                    url = url.replace("https","http")
                    body = {
                          "from": 0,
                          "size": 1,
                          "query": {
                            "match_phrase": {
                              "link": url
                            }
                          }
                        }
                    resp = es.search(index=index, doc_type=doc_type, body=body)
                    if len(resp['hits']['hits'])>0:
                        print 'ES alreay exist'
                        html = resp['hits']['hits'][0]['_source']['html']
                        self.logger.info(params["user"] + 'get weixin cached source ' + url)
                        try:
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(html, 'lxml')
                            title = soup.title.string
                        except Exception, e:
                            print Exception, params["user"] + ":", e
                            title = ""
                        status = "OK"

                        httpstatus=200
                        httpcontenttype="text/html; charset=UTF-8"

                        if (params.has_key("onlytitle") and params["onlytitle"] == "true"):
                            result = {
                                'uuid': uuid,
                                'status': status,
                                'node': node,
                                'httpstatus': httpstatus,
                                'httpcontenttype': httpcontenttype,
                                'title': title
                            }
                        else:
                            result = {
                                'uuid': uuid,
                                'status': status,
                                'node': node,
                                'httpstatus': httpstatus,
                                'httpcontenttype': httpcontenttype,
                                'html': html,
                            }
                        self.logger.info(params["user"] + 'fetched source ' + url)
                        return result

                    else:
                        import sys
                        reload(sys)
                        sys.setdefaultencoding('utf-8')
                        status = "OK"
                        httpstatus = 200
                        httpcontenttype = "text/html; charset=UTF-8"
                        #db_conn = cx_Oracle.connect('spd_dm/spd_dm_1Q#@pdb_spider')
                        #oreader = db_conn.cursor()
                        #get_status = "select status from ip_pool_proxy"
                        #oreader.execute(get_status)
                        #status_result = oreader.fetchone()
                        #oreader.close()
                        #db_conn.close()
                        try:
                            #get_proxy = "select proxy from (select * from spd_dm.ip_pool order by data_date desc) a where rownum<5"
                            get_proxy = "select proxy from spd_dm.ip_pool_v where rownum <10"
                            #select * from spd_dm.ip_pool_v where rownum <10
                            oreader.execute(get_proxy)
                            result = oreader.fetchall()
                            proxy1 = random.choice(result)[0]
                            #proxy = Proxy(
                            #    {
                            #        'proxyType': ProxyType.MANUAL,
                            #        'httpProxy': proxy1  # 代理ip和端口
                            #    }
                            #)
                            #desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
                            ## 把代理ip加入到技能中
                            #proxy.add_to_capabilities(desired_capabilities)
                            #driver = webdriver.PhantomJS(executable_path="/home/spd/app/phantomjs/phantomjs-2.1.1-linux-x86_64/bin/phantomjs",desired_capabilities=desired_capabilities)
                            #driver.get(url)
                            #driver.find_element_by_css_selector("#meta_content > em").click()
                            #html = driver.page_source
                            #driver.close()
                            #driver.quit()
                            #r = requests.get(url, proxies={"http": proxy1})
                            #html = r.text
                            proxy_handler = urllib2.ProxyHandler({"http": "%s" % proxy1, "https": "%s" % proxy1})
                            opener = urllib2.build_opener(proxy_handler)
                            html = opener.open(url, timeout=10).read()
                            py_html = pyq(html)
                            try:
                                error_message = py_html('.global_error_msg').text()
                                # print error_message
                                if "内容已被发布者删除" in error_message:
                                    result = {
                                        'uuid': uuid,
                                        'status': status,
                                        'node': node,
                                        'httpstatus': httpstatus,
                                        'httpcontenttype': httpcontenttype,
                                        'html': html,
                                    }
                                    return result
                            except Exception, e:
                                print e, params["user"] + '1'
                            try:
                                transfer_message = py_html('.weui-msg__title').text()
                                # print transfer_message
                                if "公众号已迁移" in transfer_message:
                                    result = {
                                        'uuid': uuid,
                                        'status': status,
                                        'node': node,
                                        'httpstatus': httpstatus,
                                        'httpcontenttype': httpcontenttype,
                                        'html': html,
                                    }
                                    return result
                            except Exception, e:
                                print e, params["user"] + '2'
                            try:
                                shield_message = py_html('.text_area>p').text()
                                # print shield_message
                                if "无法查看" in shield_message:
                                    result = {
                                        'uuid': uuid,
                                        'status': status,
                                        'node': node,
                                        'httpstatus': httpstatus,
                                        'httpcontenttype': httpcontenttype,
                                        'html': html,
                                    }
                                    return result
                            except Exception, e:
                                print e, params["user"] + '3'
                            try:
                                share_message = py_html('.text_area>p.tips').text()
                                # print share_message
                                if "分享" in share_message:
                                    result = {
                                        'uuid': uuid,
                                        'status': status,
                                        'node': node,
                                        'httpstatus': httpstatus,
                                        'httpcontenttype': httpcontenttype,
                                        'html': html,
                                    }
                                    return result
                            except Exception, e:
                                print e, params["user"] + '4'
                            title = py_html('#img-content>h2').text()
                            # print title
                            copyright_logo = py_html('#copyright_logo').text().split('：')[0]
                            # print copyright_logo
                            #post_date = re.findall(r'var publish_time = "(.*?)"', str(html))[0]
                            post_date = re.findall(r'",s="(.*?)"', str(html))[0]
                            # print post_date
                            msg_cdn_url = re.findall(r'var msg_cdn_url = "(.*?)"', str(html))[0]
                            #print msg_cdn_url
                            msg_cdn_id = msg_cdn_url.split('/')[4]
                            hd_head_img = re.findall(r'var hd_head_img = "(.*?)"', str(html))
                            if len(hd_head_img) == 0:
                                hd_head_img = ''
                            else:
                                hd_head_img = hd_head_img[0].replace('\r\n', '').replace('\n', '')
                            user_name = re.findall(r'var user_name = "(.*?)"', str(html))
                            if len(user_name) == 0:
                                user_name = ''
                            else:
                                user_name = user_name[0]
                            if '-' not in post_date:
                                result = {
                                    'uuid': uuid,
                                    'status': status,
                                    'node': node,
                                    'httpstatus': httpstatus,
                                    'httpcontenttype': httpcontenttype,
                                    'html': html,
                                }
                                return result
                            if copyright_logo == '':
                                post_author = py_html('#meta_content > span.rich_media_meta.rich_media_meta_text >#js_author_name').text()
                            else:
                                post_author = py_html('#meta_content > span:nth-child(2)').text()
                            if post_author == '':
                                post_author = 'null'

                            weixin_mp_name = py_html('#meta_content>span>a').text()
                            # print weixin_mp_name
                            weixin_mp_code = py_html('#js_profile_qrcode > div > p:nth-child(3) > span').text()
                            # print weixin_mp_code
                            weixin_mp_desc = py_html('#js_profile_qrcode > div > p:nth-child(4) > span').text()
                            content = py_html('#js_content').text()
                            if len(weixin_mp_name) == len(title) == len(weixin_mp_code) == len(post_date) == 0:
                                result = {
                                    'uuid': uuid,
                                    'status': status,
                                    'node': node,
                                    'httpstatus': httpstatus,
                                    'httpcontenttype': httpcontenttype,
                                    'html': html,
                                }
                                return result
                            try:
                                save_yuqing_article(title=title, mp_name=weixin_mp_name, content=content,
                                                    post_date=post_date, link=url,
                                                    html=html, mp_code=weixin_mp_code,
                                                    mp_desc=weixin_mp_desc,
                                                    copyright_logo=copyright_logo, article_author=post_author,msg_cdn_id = msg_cdn_id,hd_head_img=hd_head_img,url=url,user_name=user_name,
                                                    crawl_time=date)
                                result = {
                                    'uuid': uuid,
                                    'status': status,
                                    'node': node,
                                    'httpstatus': httpstatus,
                                    'httpcontenttype': httpcontenttype,
                                    'html': html,
                                }
                                return result
                            except Exception, e:
                                print e, params["user"] + '5'
                                return
                        except Exception, e:
                            print e, params["user"] + '6'
                elif url.startswith("http://html2.qktoutiao.com") or url.startswith("http://html3.qktoutiao.com"):
                    #self.logger.info(str(params["url"]) + '###start###')
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
                    }
                    def get_content(py_html, url, content_id):
                        #self.logger.info(str(params["url"]) + '###contentstart###')
                        html = py_html.html()
                        title = py_html('div.article > h1').text()
                        if title == '':  # 视频
                            article = py_html('body > script:nth-child(1)').text()
                            if article:
                                try:
                                    article = json.loads(article, strict=False)
                                    content_type = article['video']['type']
                                    title = article['title']
                                    post_time = article['createTime']
                                    author_id = article['authorid']
                                    nickname = article['nickname']
                                    content = ''
                                    # is_origin,1原创,0非原创,-1视频
                                    is_origin = '-1'
                                except Exception as e:
                                    return 0
                            else:
                                return 0
                        else:
                            content_type = re.search('type:(.*?),', html)
                            content_type = content_type.group(1) if content_type else ''
                            info = py_html('div.info').text().split(' ')
                            try:
                                post_time = info[0] + ' ' + info[1]
                            except Exception as e:
                                post_time = ''
                            content = py_html('div.content').text()
                            is_origin = re.search('isOrigin:([0-1]),', html)
                            is_origin = is_origin.group(1) if is_origin else '0'
                            author_id = re.search('authorid:\'([0-9]*)\',', html)
                            author_id = author_id.group(1) if author_id else ''
                            nickname = re.search('nickname:\'(.*?)\',', html)
                            nickname = nickname.group(1) if nickname else ''

                        crawl_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        # 调用内部接口获取分类
                        zhuti = fenlei(title)
                        # 获取评论,返回json
                        comment_json = get_comment(url, content_id, crawl_time)
                        # 储存文章
                        try:
                            save_qtt_content(content_id=content_id,
                                             content_type=content_type,
                                             title=title.replace('\n', ''),
                                             zhuti=zhuti,
                                             uri=url,
                                             post_time=post_time,
                                             author_id=author_id,
                                             nickname=nickname,
                                             is_origin=is_origin,
                                             content=content,
                                             comment_json=comment_json,
                                             html=html,
                                             crawl_time=crawl_time)
                        except Exception as e:
                            self.logger.info(str(params["url"]) + 'Error save_qtt_content ' + str(e))


                    def get_comment(url, content_id, crawl_time):
                        #self.logger.info(str(params["url"]) + '###commentstart###')
                        v = re.search('&v=(.*?)[^0-9]', url)
                        v = v.group(1) if v else '0'
                        time_stamp = int(round(time.time() * 1000))
                        api_url = 'http://api.1sapp.com/comment/hotList?token=&dtu=200&xhi=200&version=' + v + '&os=android&tk=&distinct_id=&deviceCode=&content_id=' + content_id + '&_=' + str(time_stamp)
                        js = '{}'
                        try:
                            response = requests.get(api_url, headers=headers)
                            js = response.json()
                        except Exception as e:
                            return js
                        status = js.get('code')
                        if status == 0:
                            items = js.get('data')
                            if items:
                                for item in items:
                                    nickname = item['nickname']
                                    comment_id = item['comment_id']
                                    comment = item['comment']
                                    post_time = item['create_time']
                                    like_num = int(item['like_num'])
                                    try:
                                        save_qtt_comment(
                                            content_id=content_id,
                                            nickname=nickname,
                                            comment_id=comment_id,
                                            comment=comment,
                                            post_time=post_time,
                                            like_num=like_num,
                                            crawl_time=crawl_time
                                        )
                                    except Exception as e:
                                        self.logger.info(str(params["url"]) + ' Error save_qtt_comment' + ' ' + str(e))
                                return str(js)
                        else:
                            return str(js)

                    def fenlei(title):
                        #self.logger.info(str(params["url"]) + '###fenleitstart###')
                        title = str(title).replace('\"', '').replace(':', '').replace(',', '').replace(';', '').replace('-', '').replace('=', '')
                        fenlei_url = "http://nlp_textclass.zj.chinamobile.com:50340/service"
                        headers = {"appId": "qtt_nlp", "token": "", "requestId": "20190220140000",
                                   "requestTime": "2019-02-20 14:00:00"}
                        post_body = '{"serviceName":"nlp_wbfl","requestParms":{"msg":"' + title + '"}}'.encode(
                            encoding='utf_8')
                        response = requests.post(fenlei_url, data=post_body, headers=headers)
                        zhuti = ''
                        try:
                            data = json.loads(response.text, encoding='utf-8')
                            result = data['respInfo']['response'][0]
                        except Exception as e:
                            return zhuti
                        for i in result:
                            zhuti = zhuti + ' ' + (i.encode('latin-1').decode('unicode_escape'))

                        return zhuti


                    def crawl(content_id, url):
                        #self.logger.info(str(params["url"]) + '###crawlstart###')
                        try:
                            r = requests.get(url, headers=headers)
                            #self.logger.info(str(params["url"]) + '###crawl 1###')
                            content = r.content.decode('utf-8')
                        except Exception as e:
                            self.logger.info(str(params["url"]) + ' ' + str(e))
                        if content.startswith('<!DOCTYPE html>'):
                            #self.logger.info(str(params["url"]) + '###crawl 3###')
                            py_html = pyq(content)
                            #self.logger.info(str(params["url"]) + '###crawl 4###')
                            get_content(py_html, url, content_id)


                    content_id = re.search('[0-9]{2}/([0-9]*)\.html', url)
                    if content_id:
                        content_id = content_id.group(1)
                        es = Elasticsearch(es_host)
                        index = "qtt_content"
                        doc_type = "qtt_content_type"
                        body = {
                            "query": {
                                "match_phrase": {
                                    "content_id": content_id
                                }
                            }
                        }
                        resp = es.search(index=index, doc_type=doc_type, body=body)
                        if len(resp['hits']['hits']) > 0:
                            print 'ES alreay exist'
                            html = resp['hits']['hits'][0]['_source']['html']
                            self.logger.info(params["user"] + 'get qtt cached source ' + url)
                        else:
                            crawl(content_id, url)
                            #self.logger.info(str(params["url"]) + '###end###')
                    else:
                        self.logger.info(str(params["url"]) + '###页面不存在###')
                else:
                    req = urllib2.Request(url=url, headers=headers)

            response = urllib2.urlopen(req,timeout=5)
            httpstatus = response.code
            httpcontenttype = response.info().getheader("Content-Type")

            if(params.has_key("ajax") and params["ajax"] == "true"):
                if(params.has_key("ajaxTimeout")):
                    ajaxTimeout = params["ajaxTimeout"]
                else:
                    ajaxTimeout = 8
                if(params.has_key("ajaxLoadImage")):
                    ajaxLoadImage = params["ajaxLoadImage"]
                else:
                    ajaxLoadImage = "false"
                from univider.render import Render
                render = Render()
                html = render.getDom(url,ajaxLoadImage,ajaxTimeout)
            else:
                html = response.read()

                gzipped = response.headers.get('Content-Encoding')

                if gzipped:
                    import zlib
                    html = zlib.decompress(html, 16+zlib.MAX_WBITS)

                if('GBK' in httpcontenttype or 'gbk' in httpcontenttype):
                    try:
                        html = html.decode('gbk')
                    except Exception,e:
                        print Exception,params["user"] + ":",e

            # print 'html : ' + html

            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html,'lxml')
                title = soup.title.string
            except Exception,e:
                print Exception,params["user"] + ":",e
                title = ""
            status = "OK"

            # print 'title : ' + title

        except Exception,e:
            httpstatus = 400
            httpcontenttype = ""
            title = ""
            html = ""
            status = str(Exception)+" : "+str(e)
            print Exception,params["user"] + ":",e


        if(params.has_key("onlytitle") and params["onlytitle"] == "true"):
            result = {
                'uuid':uuid,
                'status':status,
                'node':node,
                'httpstatus':httpstatus,
                'httpcontenttype':httpcontenttype,
                'title':title
            }
        else:
            result = {
                'uuid':uuid,
                'status':status,
                'node':node,
                'httpstatus':httpstatus,
                'httpcontenttype':httpcontenttype,
                'html':html,
            }

        self.logger.info(params["user"] + ' fetched source '  + str(params["url"]) +  str(httpstatus) )
        return result