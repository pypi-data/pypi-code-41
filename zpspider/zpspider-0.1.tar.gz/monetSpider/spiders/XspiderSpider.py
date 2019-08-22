# -*- coding: utf-8 -*-
import datetime
import re
from collections import OrderedDict
from urllib.parse import urlencode, urljoin

from scrapy import Spider, Request
import json

from scrapy_redis.spiders import RedisSpider

from monetSpider.items import  NewsItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Join

from monetSpider.loaders import NewsLoader


class XspiderSpider(RedisSpider):
    name = 'xspider'
    #lpush xspider:start_urls https://baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word=site:(www.people.com.cn)两会
    redis_key = 'xspider:start_urls'
    allowed_domains = ['baidu.com', 'people.com.cn']
    # start_urls = ['https://image.so.com/z?ch=beauty']
    # 系统配置
    custom_settings = {}

    def __init__(self, xspider=None, *args, **kwargs):
        super(XspiderSpider, self).__init__(*args, **kwargs)
        # TODO 从xspider解析得到所需的参数
        self.makeurl_settings = xspider.makeurl_settings
        self.parse_settings = xspider.parse_settings
        # self.datastructure = xspider.datastructure
        self.notNullColNameList = xspider.getNotNullColName()

    def start_requests(self):
        entryurls=self.makeurl_settings.get("entryUrls")
        if entryurls is not None:
            for entryurl in self.dicttolist(entryurls.get('entryUrl')):
                if not re.match(r'^https?:/{2}\w.+$', entryurl):
                    continue
                dict = self.paramdict(entryurl)
                print(entryurl)
                for param in self.makeurl_settings["params"]["param"]:
                    if dict.__contains__(param["@name"]):
                        # TODO 首先解析系统变量
                        # 解析一般变量
                        dict[param.get("@name")] = param.get("@value") or param.get('@defaultValue')
                if dict:
                    url = entryurl.split("?")[0] + "?" + urlencode(dict)
                else:
                    url = entryurl
                yield Request(url, self.parse)

    def paramdict(self, url):
        from urllib.parse import urlsplit
        split_result = urlsplit(url)
        dict = {}
        if split_result.query is None:
            return dict
        for key_value in split_result.query.split('&'):
            if not str(key_value).__contains__("="):
                continue
            print(key_value.split('='))
            k, v = key_value.split('=')
            dict[k] = v
        return dict

    def abshref(self, url, link):
        return urljoin(url, link)

    def okpageextractors(self, pageextractors, url):
        for pageextractor in pageextractors:
            if re.match(pageextractor["@urlRegex"], url):
                yield pageextractor

    def genxpath(self, regionxpath, colxpath):
        xpath = regionxpath
        if str(colxpath).startswith("//"):
            return xpath + str(colxpath)
        elif str(colxpath).startswith("/"):
            return xpath + "/" + str(colxpath)
        else:
            return xpath + "//" + str(colxpath)

    def parse(self, response):

        print("当前页：" + response.url)
        print("下一页：" + self.abshref(response.url,
                                    str(response.xpath("//a[contains(./text(),'下一页')]/@href").extract_first())))

        rnewsitem = NewsItem()
        if response.meta.__contains__("item"):
            rnewsitem.update(response.meta["item"])
        # 正则选择合适的处理器
        pageextractors = self.parse_settings["pageextractor"]
        # 获取符合条件的处理器列表
        for index, pageextractor in enumerate(self.okpageextractors(pageextractors, response.url)):
            # parse = pageextractor["parse"]
            datastored = pageextractor["@dataStored"].__eq__("true")
            last = index == len(pageextractors) - 1
            tosave = last or datastored
            hasregion = False
            self.parse_col(response, response, pageextractor, rnewsitem)

            for link in self.parse_link(response, response, pageextractor, rnewsitem, datastored, False):
                yield link
            regionlist = self.dicttolist(pageextractor.get("region"))
            if regionlist.__len__() > 0:
                hasregion = True
            for oregion in regionlist:

                # for osetcol in osetcol["setcols"]:
                #     self.genxpath(oregion.get("xpath", ""),osetcol.get("setcols").get("xpath"))
                for region in response.xpath(oregion.get("@xpath", "")):
                    newsitem = NewsItem()
                    newsitem.update(rnewsitem)
                    self.parse_col(response, region, oregion, newsitem)

                    for link in self.parse_link(response, region, oregion, newsitem, datastored, True):
                        yield link
                    if tosave and not self.hasNoneCol(newsitem):
                        newsitem["missing_data"] = "1" if nonecol else "0"
                        yield self.save(newsitem, response)
            nonecol = self.hasNoneCol(rnewsitem)
            if not hasregion and tosave and not nonecol:
                rnewsitem["missing_data"] = "1" if nonecol else "0"
                yield self.save(rnewsitem, response)

    def save(self, newsitem=NewsItem, response=None):
        newsitem["URL"] = response.url
        # newsitem["TIMESTAMP"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        newsitem["download_fileurl"] = response.url
        for col in str(newsitem):
            if col.endswith("url"):
                newsitem[col] = self.abshref(response.url, newsitem[col])
        # newsitem["download_imgurl"]=self.abshref(response.url,newsitem["download_imgurl"])
        loader = NewsLoader(item=newsitem, response=response)
        return loader.load_item()

    def parse_link(self, response, selector, extract, newsitem, datastored=False, isinner=False):
        url = response.url
        for olink in self.dicttolist(extract.get("link")):
            link = selector.xpath(olink["@xpath"]).extract_first()
            if not datastored and isinner:

                yield Request(self.abshref(url, link), callback=self.parse, meta={"item": newsitem})
            else:
                yield Request(self.abshref(url, link), callback=self.parse)

    def parse_col(self, response, selector, extract, newsitem):
        for osetcol in self.dicttolist(extract.get("setcol")):
            # tidyText() allText()等同功能
            setcol = '\n'.join(selector.xpath(osetcol.get("@xpath", "")).getall())
            if setcol is not None:
                setcol = self.clear(setcol, osetcol)
                print(osetcol["@ref"] + setcol)
                newsitem[osetcol["@ref"]] = setcol
            else:
                newsitem[osetcol["@ref"]] = None

    def clear(self, str, selector):
        regex = selector.get("@regex", "")
        if regex.__len__() == 0:
            return str
        str = re.sub("\\n", "", str)
        gs = re.match(regex, str)
        format = selector.get("@format", "{0}")
        if gs:
            if (re.match("{\d+}", format)):
                format = format.replace("{0}", gs.group())
                for i, group in enumerate(gs.groups()):
                    format = format.replace("{" + (i + 1).__str__() + "}", group)
                return format
            else:
                return gs.group()
        return str

    def hasNoneCol(self, newsitem):
        for col in self.notNullColNameList:
            if newsitem.get(col,None) is None:
                return True
        return False

    def dicttolist(self, dict):
        if isinstance(dict, list):
            return dict
        elif dict:
            return [dict]
        else:
            return []
