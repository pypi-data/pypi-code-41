# -*- coding: utf-8 -*-

from monetSpider.xspider.Xspider import Xspider

if __name__=="__main__":
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())

    # 'followall' is the name of one of the spiders of the project.
    process.crawl("xspider",domain="baidu.com",xspider=Xspider("../xml/百度两会.xml"))
    process.start()  # the script will block here until the crawling is finished
