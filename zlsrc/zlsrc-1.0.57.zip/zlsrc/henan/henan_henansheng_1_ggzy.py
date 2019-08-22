from math import ceil

import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from zlsrc.util.etl import est_tbs, est_meta, est_html




def f1(driver, num):
    locator = (By.XPATH, "//pre[contains(string(), 'href')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall(r'pageIndex=([0-9]+)', url)[0]
    # print(cnum)
    if num != int(cnum):
        locator = (By.XPATH, "//pre")
        txt1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        tj1 = json.loads(txt1)
        val1 = eval(tj1['return'])['Table']
        url = re.sub('pageIndex=[0-9]+', 'pageIndex=%d' % num, url)
        driver.get(url)
        locator = (By.XPATH, "//pre[contains(string(), 'href')]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//pre")
        txt2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        tj2 = json.loads(txt2)
        val2 = eval(tj2['return'])['Table']
        if val1 == val2:
            raise ValueError

    locator = (By.XPATH, "//pre")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    ul = json.loads(txt)
    lis = eval(ul['return'])['Table']
    data = []
    for tr in lis:
        name = tr['title']
        ggstart_time = tr['infodate']
        if 'http' in tr['href']:
            href = tr['href']
        else:
            href = 'http://hnsggzyfwpt.hndrc.gov.cn'+tr['href']
        diqu = tr['infoc']
        info = {'diqu':diqu}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    url = driver.current_url
    url = re.sub(r'/getSelect', '/getCount', url)
    url = url.replace('pageIndex=1&pageSize=22&', '')
    driver.get(url)
    locator = (By.XPATH, "//pre[contains(string(), 'return')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//pre")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    txt_json = json.loads(txt)
    total = txt_json['return']
    num = ceil(int(total)/22)
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//div[@class='ewb-left-bd'][string-length()>100]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        if '404' in driver.title:
            return '404'
        else:
            raise TimeoutError
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
    div = soup.find('div', class_='ewb-left-bd').parent
    if div == None:
        raise ValueError('div is None')
    return div


data = [
    ["gcjs_zhaobiao_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002001001&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_biangeng_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002001002&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002001003&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002001004&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["zfcg_zhaobiao_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002002001&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002002002&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002002003&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["jqita_zhaobiao_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002006001&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg", "http://hnsggzyfwpt.hndrc.gov.cn/services/hl/getSelect?response=application/json&pageIndex=1&pageSize=22&day=&sheng=x1&qu=&xian=&title=&timestart=&timeend=&categorynum=002006002&siteguid=9f5b36de-4e8f-4fd6-b3a1-a8e08b38ea38",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河南省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_henan_henan1"], total=2, headless=True, num=1)

    #
    # for d in data:
    #     # driver=webdriver.Chrome()
    #     url=d[1]
    #     # print(url)
    #     # driver.get(url)
    #     # df = d[-1](driver)
    #     # print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=d[-2](driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)

