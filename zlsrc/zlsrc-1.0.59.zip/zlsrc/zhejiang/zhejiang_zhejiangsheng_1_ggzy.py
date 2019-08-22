import random
from math import ceil
import pandas as pd
import re
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.fake_useragent import UserAgent
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large

ua = UserAgent()

def f1(driver, num):
    url = driver.current_url
    url = re.sub('pn=[0-9]+', 'pn=%d' % (num-1), url)
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    timeOut = 60
    if proxies:
        res = requests.get(url=url, headers=headers, proxies=proxies, timeout=timeOut)
    else:
        res = requests.get(url=url, headers=headers, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.content.decode('utf-8')
        txt_json = json.loads(html)
        lis = txt_json['result']['records']
        data = []
        for tr in lis:
            name = tr['title']
            ggstart_time = tr['date']
            if 'http' in tr['link']:
                href = tr['link']
            else:
                href = 'http://www.zjpubservice.com'+tr['link']
            diqu = tr['remark5']
            info = {'diqu':diqu}
            info = json.dumps(info, ensure_ascii=False)
            tmp = [name, ggstart_time, href, info]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        return df



def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = {}
    url = driver.current_url
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    # 下载超时
    timeOut = 60
    if proxies:
        res = requests.get(url=url, headers=headers, proxies=proxies, timeout=timeOut)
    else:
        res = requests.get(url=url, headers=headers, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.content.decode('utf-8')
        # print(html)
        txt_json = json.loads(html)
        total = txt_json['result']['totalcount']
        num = ceil(int(total)/15)
        driver.quit()
        return int(num)



def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    try:
        locator = (By.XPATH, "//div[@class='article_con'][string-length()>100]")
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))
    except:
        locator = (By.XPATH, "//body[string-length()=0]")
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))
        locator = (By.XPATH, "//head[string-length()=0]")
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located(locator))
        if 'citycode=undefined' not in driver.current_url:
            return '网页不可爬取'
    locator = (By.XPATH, "//div[@class='article_con'][string-length()>100]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.5)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div' ,class_='article_bd')

    if div == None:raise ValueError
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002001001&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgys_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002001002&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kaibiao_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002001003&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002001004&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002001005&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002002001&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002002002&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ###
    ["jqita_zhaobiao_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002005001&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://zjpubservice.zjzwfw.gov.cn/fulltextsearch/rest/getfulltextdata?format=json&sort=0&rmk1=002005002&pn=0&rn=15&idx_cgy=web",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="浙江省", **args)
    est_html(conp, f=f3, **args)

# 修改日期：2019/8/16
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_zhejiang_zhejiang"])


    # for d in data[4:]:
    #     # driver=webdriver.Chrome()
    #     url=d[1]
    #     # print(url)
    #     # driver.get(url)
    #     # df = f2(driver)
    #     # print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         print(f)
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, ' http://www.zjpubservice.com/jump.html?infoid=00447a3a-9fe5-4a5d-a58a-81d13aa029d8&categorynum=002001004&infodate=20170123')
    # print(df)
    # driver.quit()

