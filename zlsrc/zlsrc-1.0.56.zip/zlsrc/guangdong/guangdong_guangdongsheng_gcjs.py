import json
import math
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.fake_useragent import UserAgent
from zlsrc.util.etl import est_meta, est_html, add_info

ua = UserAgent()
proxy = ''
def get_ip():
    global proxy
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)
        ip = r.text
        proxy = {'http': ip}
    except:
        proxy = {}
    return proxy


def requests_hb(post_url, post_data):

    global proxy
    if proxy == {}:get_ip()
    try:
        content = requests.post(post_url, data=post_data, headers={"User-Agent": ua.random}, timeout=60, proxies=proxy)
    except:
        proxy = get_ip()
        content = requests.post(post_url, data=post_data, headers={"User-Agent": ua.random}, timeout=60, proxies=proxy)
    return content


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='main_info']")
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
    div = soup.find('div', class_="main_info")
    return div


def f1(driver, num):
    type = driver.current_url.split('list')[1]
    param = {
    'draw': '1',
    'columns[0][data]': 'id',
    'columns[0][name]':'',
    'columns[0][searchable]': 'true',
    'columns[0][orderable]': 'false',
    'columns[0][search][value]':'',
    'columns[0][search][regex]': 'false',
    'start': '0',
    'length': '20',
    'search[value]':'',
    'search[regex]': 'false',
    'page': str(num),
    'type': type.lower(),
    'xmmc':'',
    'rows': '20'}

    contents = json.loads(requests_hb(driver.current_url,param).text)['data']

    data = []
    for content in contents:
        area = content.get('szdq')
        name = content.get('title')
        ggstart_time = content.get('createDate')
        ggtype = content.get('type')

        url = 'http://zbtb.gd.gov.cn/bid/detail' + type + "?id=" +content.get('id')
        info = json.dumps({'area':area,'ggtype':ggtype},ensure_ascii=False)
        temp = [name, ggstart_time, url,info]

        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    type = driver.current_url.split('list')[1].lower()
    param = {
    'draw': '1',
    'columns[0][data]': 'id',
    'columns[0][name]':'',
    'columns[0][searchable]': 'true',
    'columns[0][orderable]': 'false',
    'columns[0][search][value]':'',
    'columns[0][search][regex]': 'false',
    'start': '0',
    'length': '20',
    'search[value]':'',
    'search[regex]': 'false',
    'page': '1',
    'type': type,
    'xmmc':'',
    'rows': '20'}

    content = json.loads(requests_hb(driver.current_url,param).text)


    total_page = math.ceil(int(content['recordsTotal'])/20)
    driver.quit()
    return int(total_page)


data = [
    #
    ["gcjs_zgys_gg",
     "http://zbtb.gd.gov.cn/bid/listZgysgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zgysjg_gg",
     "http://zbtb.gd.gov.cn/bid/listZgscbg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_zhaobiao_gg",
     "http://zbtb.gd.gov.cn/bid/listZbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_gqita_pb_gg",
     "http://zbtb.gd.gov.cn/bid/listPbbg",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"评标"}), f2],
    #
    ["gcjs_zhongbiaohx_gg",
     "http://zbtb.gd.gov.cn/bid/listZbhxrgs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_zhongbiao_gg",
     "http://zbtb.gd.gov.cn/bid/listZbjg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="广东省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    # for d in data:
    #
    #     driver = webdriver.Chrome()
    #     url = d[1]
    #     driver.get(url)
    #     df = f1(driver, 2)
    #     #
    #     for u in df.values.tolist()[:4]:
    #         print(f3(driver, u[2]))
    #     driver.get(url)
    #
    #     print(f2(driver))

    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "guangdongsheng"])
