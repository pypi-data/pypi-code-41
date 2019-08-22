import json
from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html, add_info, est_meta_large


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@width='1002']/tbody/tr/td/table[@width='930']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    before = len(driver.page_source)
    time.sleep(0.1)
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
    div = soup.find_all('table', width='930')[0]
    return div


def f1(driver, num):

    locator = (By.XPATH, "//tr[@id='biaoti'][1]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    url = driver.current_url
    mark=re.findall('perpage=(\d+)&',url)[0]
    if int(num) != int(total_page):
        locator = (By.XPATH, '//table[@id="moredingannctable"]/tbody[count(tr)=%s]'%(int(mark)*2))
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

    val = driver.find_element_by_xpath("//tr[@id='biaoti'][1]//a").get_attribute("href")[-30:]

    cnum = int(driver.find_element_by_xpath("//div[@id='outlinebar']/span").text)

    if int(cnum) != int(num):
        url = re.sub('(?<=search\?page=)\d+', str(num), url)
        driver.get(url)
        locator = (By.XPATH, '//tr[@id="biaoti"][1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        locator = (By.XPATH, '//table[@id="moredingannctable"]/tbody[count(tr)=%s]'%(int(mark)*2))
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//tr[@id='biaoti']")
    date_time_list = body.xpath("//tr[@bgcolor='#E3EDF6']")
    for content, date in zip(content_list, date_time_list):
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = date.xpath("./td[2]/span[1]/text()")[0].strip()
        url = content.xpath("./td/a/@href")[0]
        area = date.xpath("./td[2]/span[2]/text()")[0].strip()
        purchaser = date.xpath("./td[2]/span[3]/text()")[0].strip()
        info = json.dumps({'diqu': area, "purchaser": purchaser}, ensure_ascii=False)
        temp = [name, ggstart_time, url, info]
        # print(temp)

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    global total_page
    locator = (By.XPATH, '//table[@id="moredingannctable"]//tr[1]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    try:
        locator = (By.XPATH, '//a[@class="last-page"]')
        txt = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')
        total_page = int(re.findall('page=(\d+)',txt)[0])
    except:
        url=driver.current_url
        mark = re.findall('perpage=(\d+)&', url)[0]
        url=re.sub('perpage=\d+&',"perpage=1&",url)
        driver.get(url)
        locator = (By.XPATH, '//table[@id="moredingannctable"]//tr[1]//a')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, '//a[@class="last-page"]')
        txt = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')
        total_page = re.findall('page=(\d+)', txt)[0]
        if int(total_page) <= int(mark):
            total_page=1
        else:
            raise TimeoutError

    driver.quit()
    return int(total_page)



def get_data():
    data = []

    #zfcg
    ggtype3 = OrderedDict([("zhaobiao", "zbgg"), ("biangeng", "gzgg"), ("zhongbiao", "zhbgg"), ("liubiao", "fbgg")])

    adtype1 = OrderedDict([('省本级', '130000000'), ("石家庄市", "130100000"), ("承德市", "130800000"), ("张家口市", "130700000"), ("秦皇岛市", "130300000"),
                           ('唐山市', '130200000'), ("廊坊市", "131000000"), ("保定市", "130600000"), ("沧州市","130900000"),("衡水市","131100000"),
                           ("邢台市","130500000"),("邯郸市","130400000"),("定州市","130682000"),("辛集市","130181000"),("雄安新区","139900000")])

    # zfcg
    for w1 in ggtype3.keys():
        for w2 in adtype1.keys():
            href = "http://search.hebcz.cn:8080/was5/web/search?page=1&channelid=228483&perpage=20&outlinepage=10&lanmu={jt}&admindivcode={dq}".format(
                jt=ggtype3[w1],dq=adtype1[w2])

            tmp = ["zfcg_{0}_diqu{1}_gg".format(w1, adtype1[w2]), href, ["name", "ggstart_time", "href", 'info'],
                   f1, f2]
            data.append(tmp)

    data1 = data.copy()

    data2=[

        ["zfcg_dyly_gg",
         "http://search.hebcz.cn:8080/was5/web/search?page=1&channelid=228483&perpage=20&outlinepage=10&lanmu=dyly",
         ["name", "ggstart_time", "href", "info"], f1, f2],
    ]
    data1.extend(data2)

    return data1

data=get_data()


##中国河北政府采购网
def work(conp, **arg):
    est_meta_large(conp, data=data,interval_page=800, diqu="河北省", **arg)
    est_html(conp, f=f3, **arg)

#http://www.ccgp-hebei.gov.cn/province/cggg/zhbgg/

if __name__ == '__main__':
    # conp = ["postgres", "since2015", "192.168.4.198", "hebei", "hebei_hebeisheng_zfcg"]
    conp = ["postgres", "since2015", "192.168.3.171", "test", "lch"]
    work(conp=conp,pageloadstrategy="none",ipNum=0,pageloadtimeout=80,image_show_gg=2,num=1,headless=False)
    # url = "http://search.hebcz.cn:8080/was5/web/search?page=1&channelid=228483&perpage=50&outlinepage=10&lanmu=zbgg"
    # driver = webdriver.Chrome()
    #
    # driver.get(url)
    # f1(driver,2)
    # print(f2(driver))