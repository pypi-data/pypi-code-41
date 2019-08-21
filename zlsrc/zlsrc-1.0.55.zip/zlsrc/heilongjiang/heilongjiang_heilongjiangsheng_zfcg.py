import json

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from zlsrc.util.etl import est_meta, est_html, add_info
from zlsrc.util.fake_useragent import UserAgent

cookies = ''
form_data1 ={}
form_data = {
    # 'lbbh': '4',
    'id': '110',
    'xwzsPage.zlbh': '',
}

ua = UserAgent()
headers = {
    'Cookie': 'COLLCK=1735242673;JSESSIONID=0hyjcvGTnnQ1GQbHqyBPLcQtpBlWQJRJZNx7ypskCwXktyDly255!-1523611838;',
    'User-Agent': ua.random,

}


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='xxej'][string-length()>50]")
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
    div = soup.find('div', class_='xxej')

    return div


def f1_bk(driver, num):
    '''{
    'xwzsPage.pageNo': '1',
    'xwzsPage.pageSize': '20',
    'xwzsPage.pageCount': '1514',
    'lbbh': '4',
    'id': '110',
    'xwzsPage.LBBH': '4',
    }'''
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = {}
    
    form_data1['xwzsPage.pageNo'] = num
    url = driver.current_url.split('?')[0]
    response = requests.post(url, headers=headers, data=form_data1,proxies=proxies,timeout=40)
    if response.status_code != 200:
        raise ValueError('error response status code %s'%response.status_code)
    response = response.text

    data = []

    body = etree.HTML(response)
    content_list = body.xpath('//div[@class="yahoo"]/div')

    for content in content_list:
        name = content.xpath("./span[@class='lbej']/a/text()")[0].strip()
        ggstart_time = content.xpath("./span[@class='sjej']/text()")[0].strip()
        href = 'http://www.hljcg.gov.cn' + re.findall(r"href='([^']+)'", content.xpath("./span[@class='lbej']/a/@onclick")[0])[0]
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df
def f1(driver, num):
    locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//div[@class="yahoo2"]/div/span/b[2]').text.strip()
    cnum = re.findall('(\d+)/', cnum)[0]
    if int(cnum) != num:
        val = driver.find_element_by_xpath('//div[@class="yahoo"]/div[1]/span/a').get_attribute('onclick')[-40:-15]
        driver.execute_script("javascript:jump('{}');return false;".format(num))
        locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a[not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='yahoo')
    divs = div.find_all('div', class_="xxei")

    for li in divs:
        href = li.find('span', class_="lbej").a['onclick']
        name = li.find('span', class_="lbej").a.get_text()
        ggstart_time = li.find('span', class_="sjej").get_text()

        href = re.findall('javascript:location.href=(.+);return false', href)[0].strip("'")

        if 'http' in href:
            href = href
        else:
            href = 'http://www.hljcg.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df['info']=None
    return df

def f2_bk(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = {}
    global cookies,form_data1
    form_data1 = form_data.copy()
    lbbh = driver.current_url.split('?')[1]
    url = driver.current_url.split('?')[0]

    home_url = 'http://www.hljcg.gov.cn/home.jsp'
    driver.get(home_url)

    driver.execute_script('window.scrollBy(250,0)')

    driver.find_element_by_class_name('sbj_btn').click()

    cookies = ''
    for dict1 in driver.get_cookies():
        cookies += dict1['name'] + '='
        cookies += dict1['value'] + ';'

    headers['Cookie'] = cookies
    form_data1['lbbh'] = lbbh
    response = requests.post(url, headers=headers,proxies=proxies, data=form_data1,timeout=40)

    if response.status_code != 200:
        raise ValueError('error response status code %s'%response.status_code)
    response=response.text

    body = etree.HTML(response)

    total_page = re.findall('/(\d+)', body.xpath('//div[@class="list-page-detail"]/span/b[2]/text()')[0])[0]
    driver.quit()
    form_data1['xwzsPage.pageCount'] = total_page
    form_data1['xwzsPage.pageSize'] = 20
    form_data1['xwzsPage.LBBH'] = lbbh
    form_data1['xwzsPage.GJZ'] = ''

    return int(total_page)

def f2(driver):
    locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//div[@class="list-page-detail"]/span/b[2]').text
    total=re.findall('1/(\d+)',total)[0]
    driver.quit()

    return int(total)

def chang_type(f,mark):
    def inner(*args):
        driver=args[0]
        WebDriverWait(driver, 10).until(lambda driver:"http" in driver.current_url)

        curl=driver.current_url

        if "http://www.hljcg.gov.cn/index.jsp" == curl:

            driver.get('http://www.hljcg.gov.cn/home.jsp')

            locator = (By.XPATH, '//div[@class="sbj_btn"]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

            driver.execute_script("queryDqdm('23');return false;")
            locator = (By.XPATH, '//div[@class="cen_new"]//ul/li[1]//a')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            driver.execute_script("onedet('%s','')"%mark)

            locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner



data_bk = [
    # http://www.hljcg.gov.cn/xwzs!queryGd.action?4
    ["zfcg_zhaobiao_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?4",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yucai_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?99",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?5",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # biangeng 包括流标废标
    ["zfcg_gqita_bian_liu_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?30",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_dyly_gg", "http://www.hljcg.gov.cn/xwzs!queryGd.action?98",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


data=[
["zfcg_zhaobiao_gg","http://www.hljcg.gov.cn/index.jsp",["name","ggstart_time","href","info"],chang_type(f1,4),chang_type(f2,4)],
["zfcg_yucai_gg","http://www.hljcg.gov.cn/index.jsp",["name","ggstart_time","href","info"],chang_type(f1,99),chang_type(f2,99)],
["zfcg_dyly_gg","http://www.hljcg.gov.cn/index.jsp",["name","ggstart_time","href","info"],chang_type(f1,98),chang_type(f2,98)],
##包含流标，变更
["zfcg_gqita_liu_bian_gg","http://www.hljcg.gov.cn/index.jsp",["name","ggstart_time","href","info"],chang_type(f1,30),chang_type(f1,30)],
["zfcg_zhongbiao_gg","http://www.hljcg.gov.cn/index.jsp",["name","ggstart_time","href","info"],chang_type(f1,5),chang_type(f1,5)],
]



def work(conp, **arg):
    est_meta(conp, data=data, diqu="黑龙江省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "heilongjiang"], pageloadtimeout=60,pageloadstrategy='none',num=1,headless=False,ipNum=0)

