import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from zlsrc.util.etl import est_meta, est_html, add_info


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//*[@id="content"]/div/div[2]/div')
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
    div = soup.find('div', class_='content-text')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//pre[contains(string(), 's2')]")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    page = driver.page_source
    try:
        cnum = int(re.findall("&lt;option value=\'\d+?\' selected=\'selected\'&gt;第(\d+)页&lt;", page)[0])
    except:
        cnum = 1
    if cnum != int(num):
        url = driver.current_url
        url = re.sub("pageNo=\d+", "pageNo=" + str(num), url)
        driver.get(url)

    data = []
    page = driver.page_source
    href_list = re.findall("href='(/.+?)'", page)
    ggtime_list = re.findall("s2'&gt;(.+?)&lt;", page)
    title_list = re.findall("'_blank'&gt;(.+?)&lt;", page)
    for href, time, title in zip(href_list, ggtime_list, title_list):
        temp = [title, time, 'http://zfcg.huhhot.gov.cn' + href]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//pre[contains(string(), 's2')]")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    page = driver.page_source
    try:
        total_page = int(re.findall("&lt;option value=\'\d+?\'&gt;第(\d+?)页&lt;/option&gt;", page)[-1])
    except:
        total_page = 1
    return int(total_page)


data = [
    # 增加公告
    ["zfcg_biangeng_zs_benji_gg",
     "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.266.404&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'资格预审更正公告'}), f2],

    ["zfcg_biangeng_zs_qixian_gg",
     "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.267.408&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '资格预审更正公告'}), f2],

    ["zfcg_biangeng_zhongb_qixian_gg",
     "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.267.406&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'中标更正公示'}), f2],

    ####
    ["zfcg_zhaobiao_benji_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.266.269&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_benji_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.266.403&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_benji_gg",
     "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.266.270&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_benji_gg",
     "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.266.343&pageNo=1&check=null",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zgys_benji_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.266.304&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yanshou_benji_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.266.364&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_dyly_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=363&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_qixian_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.267.273&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_qixian_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.267.407&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_qixian_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.267.306&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_qixian_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.267.344&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zgys_qixian_gg", "http://zfcg.huhhot.gov.cn/huShi_web_login/showAllMessage?code=265.267.309&pageNo=1&check=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="内蒙古自治区呼和浩特市", **arg)
    est_html(conp, f=f3, **arg)

# 修改日期：2019/8/19
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "neimenggu_huhehaote"], ipNum=0, headless=False)
