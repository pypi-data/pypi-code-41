import json
import math
import re
import sys
import random
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
from zlsrc.util.fake_useragent import UserAgent
import requests
import time

"""
本网站有两种框架，两种方法爬取
"""

ua=UserAgent()
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': '218.2.208.144:8094',
    'User-Agent': ua.random
}
proxy = {}


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


def f3(driver, url):
    driver.get(url)
    if "页面不存在" in driver.page_source:
        return '页面不存在.'
    locator = (By.XPATH, "//div[@class='mainCont'] | //div[@class='panel'] | //div[@id='body']|//div[@id='sch_box']")
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
    div = soup.find('div', class_='mainCont')
    if div == None:
        div = soup.find('div', class_='panel')
        if div == None:
            div = soup.find('div', id="body")
            if div == None:
                div = soup.find('div', id="sch_box")
    return div



def f1(driver, num):
    if "ztzl" in driver.current_url:
        locator = (By.XPATH, '//*[@id="ny_cg01"]/div/ul/li[1]/a|//div[@class="Main_List"]/ul/li[1]')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        val = driver.find_element_by_xpath('//*[@id="ny_cg01"]/div/ul/li[1]/a|//div[@class="Main_List"]/ul/li[1]/a').get_attribute("href")[-25:]

        locator = (By.XPATH, "//a[@class='this']|//div[@class='pageNum']")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        if "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg" in driver.current_url:
            cnum = driver.find_element_by_xpath("//div[@class='pageNum']/p/span[1]").text.split('/')[0]
        else:
            cnum = driver.find_element_by_xpath("//a[@class='this']").text
        if int(cnum) != int(num):
            if "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg" in driver.current_url:
                driver.execute_script("dataSeD.loadData(%s)" % num)
            else:
                new_url = re.sub('index[_\d]*\.', 'index_' + str(num) + '.' if num != 1 else 'index.',driver.current_url)
                driver.get(new_url)
            locator = (By.XPATH, '//*[@id="ny_cg01"]/div/ul/li[1]/a[not(contains(@href,"%s"))]|//div[@class="Main_List"]/ul/li[1]/a[not(contains(@href,"%s"))]' % (val, val))
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))

        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//*[@id="ny_cg01"]/div/ul/li|//div[@class="Main_List"]/ul/li')
        for content in content_list:
            name = content.xpath("./a/text()")[0].strip()
            ggstart_time = content.xpath("./span/text()")[0].strip('(').strip(")")
            url = content.xpath("./a/@href")[0]
            if 'http://' not in url:
                if "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg" in driver.current_url:
                    url = "http://cz.wuxi.gov.cn" + url
                else:
                    url = "http://xzfw.wuxi.gov.cn" + url
            temp = [name, ggstart_time, url]
            data.append(temp)
        df = pd.DataFrame(data=data)
        df['info'] = None
        return df

    elif "informs" in driver.current_url:
        val = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(
            (By.XPATH, '//div[@id="sch_box"]/div[contains(@style,"padding")]/li[1]/a'))).get_attribute('href')[-10:]
        cnum = int(WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//span[@class="page current"]'))).text.strip())
        if int(cnum) != int(num):
            url = re.sub('page=\d+', 'page=' + str(num), driver.current_url)
            driver.get(url)
            locator = (By.XPATH, '//div[@id="sch_box"]/div[contains(@style,"padding")]/li[1]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 20).until(EC.visibility_of_any_elements_located(locator))
        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//div[@id="sch_box"]/div[contains(@style,"padding")]/li')
        for content in content_list:
            name = content.xpath('./a/text()')[0].strip()
            ggstart_time = content.xpath("./span/text()")[0].strip('(').strip(")")
            url = "http://dzhcg.sinopr.org" + content.xpath("./a/@href")[0]
            temp = [name, ggstart_time, url]
            data.append(temp)
        df = pd.DataFrame(data=data)
        df['info'] = None

        return df

    else:
        global proxy

        driver_info = webdriver.DesiredCapabilities.CHROME
        data = {"page": num, "rows": 20}

        try:
            if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
                proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
                proxies = {proxy_ip[0]: proxy_ip[1]}
                page = requests.post(driver.current_url, data=data, proxies=proxies, headers=headers, timeout=40).text
            else:
                if proxy == {}: get_ip()
                page = requests.post(driver.current_url, data=data, headers=headers, timeout=40, proxies=proxy).text
        except:
            try:
                page = requests.post(driver.current_url, data=data, headers=headers, timeout=40, proxies=proxy).text
            except:
                get_ip()
                page = requests.post(driver.current_url, data=data, headers=headers, timeout=40, proxies=proxy).text


        data1 = []
        # print(json.loads(page))
        content_list = json.loads(page).get('rows')
        for content in content_list:
            if "placard_type=" in driver.current_url:
                ggstart_time = content.get('sign_start_date')
                name = content.get("placard_name")
                url = 'http://218.2.208.144:8094/EBTS/publish/announcement/doEdit?proId=' + content.get("placard_id")
                tender_project_type = content.get("tender_project_type")
                sign_end_date = content.get("sign_end_date")
                info = json.dumps({"ggtype": tender_project_type, "ggend_time": sign_end_date}, ensure_ascii=False)

            elif "placardQueryList" in driver.current_url:
                ggstart_time = content.get('check_publish_send_date')
                name = content.get("placard_name")
                url = 'http://218.2.208.144:8094/EBTS/publish/announcement/placarddetail?id=' + content.get("tender_id")
                company = content.get("bid_unit_name")
                sign_end_date = content.get("check_end_date")
                area = content.get("check_area")
                info = json.dumps({"company": company, "ggend_time": sign_end_date, "area": area}, ensure_ascii=False)

            elif driver.current_url[-5:] == "query":
                ggstart_time = content.get('zb_placard_send_date')
                name = content.get("zb_placard_name")
                url = 'http://218.2.208.144:8094/EBTS/publish/announcement/edit?str=' + content.get("zb_placard_id") + ',' + content.get("zb_placard_flag")
                company = content.get("zb_unit_name")
                sign_end_date = content.get("check_end_date")
                fabu_danwei = content.get("bid_unit_name")
                agents_name = content.get("agent_unit_name")
                info = json.dumps({"zhongbiao_danwei": company, "ggend_time": sign_end_date, "fabu_danwei": fabu_danwei,
                                   "agents_name": agents_name}, ensure_ascii=False)


            elif "searchFlgMenu" in driver.current_url:
                ggstart_time = content.get('publish_date')
                name = content.get("project_name")
                tenderId = content.get("tender_id")
                reBidNumber = content.get("re_bid_number")
                url = "http://218.2.208.144:8094/EBTS/publish/announcement/confirmDoDetail?tenderId=" + tenderId + "&reBidNumber=" + str(
                    reBidNumber)
                zhaobiao_danwei = content.get("enterprise_name")
                info = json.dumps({"zhaobiao_danwei": zhaobiao_danwei}, ensure_ascii=False)
            if not name:name = 'None'
            if not ggstart_time:ggstart_time = 'None'
            if not url:url = 'None'
            temp = [name, ggstart_time, url, info]
            data1.append(temp)
            df = pd.DataFrame(data=data1)

        return df


def f2(driver):
    if 'ztzl' in driver.current_url:
        if "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg" in driver.current_url:
            total_page = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='pageNum']/p/span[1]"))).text.split('/')[1]
        else:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, 'pages')))
            total_page = driver.find_element_by_xpath('//div[@id="pages"]').text.split('\n')[0][2:-1]
    elif "informs" in driver.current_url:
        total_page = re.findall('page=(\d+)', WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//span[@class="last"]/a'))).get_attribute("href"))[0]

    else:
        driver_info = webdriver.DesiredCapabilities.CHROME
        data = {"page": 10, "rows": 20}
        global proxy
        try:
            if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
                proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1]
                content = json.loads(requests.post(driver.current_url, data=data, proxies=proxy_ip, headers=headers, timeout=40).text)
            else:
                if proxy=={}:proxy = get_ip()
                content = json.loads(requests.post(driver.current_url, data=data, headers=headers, timeout=40).text)
        except:
            try:
                content = json.loads(requests.post(driver.current_url, data=data, headers=headers, timeout=40, proxies=proxy).text)
            except:
                proxy = get_ip()
                content = json.loads(requests.post(driver.current_url, data=data, headers=headers, timeout=40, proxies=proxy).text)
        total_page = math.ceil(int(content.get('total')) / 20)
    driver.quit()

    return int(total_page)


data = [

    ["gcjs_zhaobiao_sj_gc_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/sjzx/zbgg/gcl/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "工程"}), f2],
    ["gcjs_zhaobiao_sj_fgc_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/sjzx/zbgg/fgcl/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "非工程"}), f2],
    ["gcjs_zhaobiao_qj_gc_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/qfzx/zbgg/gcl/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "工程"}), f2],
    ["gcjs_zhaobiao_qj_fgc_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/qfzx/zbgg/fgcl/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "非工程"}), f2],

    ["gcjs_zhongbiaohx_qj_gc_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/qfzx/pbjggs/gcl/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "工程"}), f2],
    ["gcjs_zhongbiaohx_qj_fgc_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/qfzx/pbjggs/fgcl/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "非工程"}), f2],
    ["gcjs_zhongbiaohx_sj_gc_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/sjzx/zbhxrgs/gcl/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "工程"}), f2],
    ["gcjs_zhongbiaohx_sj_fgc_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/sjzx/zbhxrgs/fgcl/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "非工程"}), f2],

    ["gcjs_zhongbiao_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/sjzx/zbjggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["gcjs_zhongbiao_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/qfzx/zbjggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],

    ["gcjs_zgysjg_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/qfzx/zgysgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],
    ["gcjs_zgysjg_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/sjzx/zgysgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],

    ["gcjs_kongzhijia_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/sjzx/zgxjgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["gcjs_kongzhijia_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/qfzx/zgxjgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],

    ["gcjs_zhaobiao_zjfb_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/qfzx/zjfbjggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],
    ["gcjs_zhaobiao_zjfb_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/jsgc/sjzx/zjfbjggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],

    ["zfcg_zhaobiao_hw_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cghwgg1/cghwgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "货物"}), f2],
    ["zfcg_biangeng_hw_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cghwgg1/cghwgzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "货物"}), f2],
    ["zfcg_zhongbiao_hw_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cghwgg1/cghwzbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "货物"}), f2],

    ["zfcg_zhaobiao_hw_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cghwgg/cghwgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "货物"}), f2],
    ["zfcg_biangeng_hw_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cghwgg/cghwgzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "货物"}), f2],
    ["zfcg_zhongbiao_hw_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cghwgg/cghwzbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "货物"}), f2],

    ["zfcg_zhaobiao_fw_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cgfwgg2/cgfwgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "服务"}), f2],
    ["zfcg_biangeng_fw_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cgfwgg2/cgfwgzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "服务"}), f2],
    ["zfcg_zhongbiao_fw_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cgfwgg2/cghwzbgg1/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级", "type": "服务"}), f2],

    ["zfcg_zhaobiao_fw_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cgfwgg/cgfwgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "服务"}), f2],
    ["zfcg_biangeng_fw_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cgfwgg/cgfwgzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "服务"}), f2],
    ["zfcg_gqita_zhong_liu_fw_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cgfwgg/cgfwzbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心", "type": "服务"}), f2],

    ######
    ["zfcg_zhaobiao_gc_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cggcgg/cgfwgg1/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["zfcg_biangeng_gc_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cggcgg/cgfwgzgg1/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["zfcg_gqita_zhong_liu_gc_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/sj/cggcgg/cggczbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["zfcg_zhaobiao_gc_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cggcgg/cggcgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],
    ["zfcg_biangeng_gc_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cggcgg/cggcgzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],
    ["zfcg_gqita_zhong_liu_gc_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/zfcg/qfzx/cggcgg/cggczbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],

    ["gcjs_shuili_zhaobiao_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/slgc/sj/zbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["gcjs_shuili_zhaobiao_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/slgc/qj/zbgg3/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],
    ["gcjs_shuili_kongzhijia_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/slgc/qj/zgxjgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],
    ["gcjs_shuili_kongzhijia_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/slgc/sj/zgxjgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["gcjs_shuili_zhongbiaohx_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/slgc/sj/zbgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["gcjs_shuili_zhongbiao_sj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/slgc/sj/zbrgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "市级"}), f2],
    ["gcjs_shuili_zhongbiaohx_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/slgc/qj/zbgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],
    ["gcjs_shuili_zhongbiao_qj_gg", "http://xzfw.wuxi.gov.cn/ztzl/wxsggzyjyzx/slgc/qj/zbrgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area": "分区中心"}), f2],
    #
    # # http://218.2.208.144:8094/EBTS//publish/announcement/paglist?type=1
    ["zfcg_jiaotong_zhaobiao_gg", "http://218.2.208.144:8094/EBTS/publish/announcement/getList?placard_type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_jiaotong_zgys_gg", "http://218.2.208.144:8094/EBTS/publish/announcement/getList?placard_type=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_jiaotong_gqita_pingbiao_gg", "http://218.2.208.144:8094/EBTS/publish/announcement/placardQueryList",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_jiaotong_zhongbiao_gg", "http://218.2.208.144:8094/EBTS/publish/announcement/query",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_jiaotong_zgysjg_gg", "http://218.2.208.144:8094/EBTS/publish/announcement/queryConfirm?searchFlgMenu=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/cggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/gzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_zhong_liu_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/cjgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yucai_gg", "http://cz.wuxi.gov.cn/ztzl/zfcg/cgxxgg/cgyg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yanshou_gg", "http://dzhcg.sinopr.org/informs/cgxxgg.html?page=2&type=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="江苏省无锡市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    # conp = ["postgres", "since2015", "192.168.3.171", "jiangsu", "wuxi"]
    # work(conp, headless=False,num=2,pageloadtimetou=60,)
    for i in data:
        driver = webdriver.Chrome()
        driver.get(i[1])
        df = f1(driver,1).values.tolist()
        print(df)
        for k in df[:2]:
            f3(driver,k[2])
        driver.get(i[1])
        print(f2(driver))