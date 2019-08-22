import pandas as pd
import re

from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zlsrc.util.etl import est_meta, est_html, add_info
import time



def f1(driver, num):
    val = driver.find_element_by_xpath("//div[@class='ewb-info']/ul/li[1]/div/a").get_attribute('href')[-70:]

    driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',%s)" % num)
    if "ewb-page-items clearfix" in driver.page_source:
        cnum = int(driver.find_element_by_xpath("//li[@class='ewb-page-li page first current']/a").text)
    else:
        cnum = 1
    if int(num) != int(cnum):

        locator = (By.XPATH, "//div[@class='ewb-info']/ul/li[1]/div/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source

    body = etree.HTML(page)

    contents = body.xpath("//div[@class='ewb-info']/ul/li")

    data = []
    for content in contents:
        name = content.xpath("./div/a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        href = "http://ggzyjy.yichang.gov.cn/" + content.xpath("./div/a/@href")[0].strip()
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//li[@class="ewb-page-li ewb-page-noborder ewb-page-num"]/span')

    if "ewb-page-items clearfix" in driver.page_source:
        txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

        total = re.findall('\/(\d+)', txt)[0]
    else:
        total = 1

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='detail-main']")

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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

    soup = BeautifulSoup(page, 'lxml')

    div = soup.find('div', class_='detail-main')

    return div


data = [

    ["gcjs_shigong_zhaobiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001001/003001001001/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "施工"}), f2],

    ["gcjs_jianli_zhaobiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001001/003001001002/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "监理"}), f2],

    ["gcjs_kancha_zhaobiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001001/003001001003/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "勘察"}), f2],

    ["gcjs_gcqita_zhaobiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001001/003001001004/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "其它"}), f2],

    ["gcjs_shigong_biangeng_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001002/003001002001/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "施工"}), f2],

    ["gcjs_jianli_biangeng_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001002/003001002002/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "监理"}), f2],

    ["gcjs_kancha_biangeng_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001002/003001002003/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "勘察"}), f2],

    ["gcjs_gcqita_biangeng_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001002/003001002004/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "其它"}), f2],

    ["gcjs_shigong_zhongbiaohx_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001003/003001003001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gctype": "施工"}), f2],

    ["gcjs_jianli_zhongbiaohx_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001003/003001003002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gctype": "监理"}), f2],

    ["gcjs_kancha_zhongbiaohx_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001003/003001003003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gctype": "勘察"}), f2],

    ["gcjs_gcqita_zhongbiaohx_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001003/003001003004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gctype": "其它"}), f2],

    ["gcjs_shigong_zhongbiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001004/003001004001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gctype": "施工"}), f2],

    ["gcjs_jianli_zhongbiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001004/003001004002/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "监理"}), f2],

    ["gcjs_kancha_zhongbiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001004/003001004003/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "勘察"}), f2],

    ["gcjs_gcqita_zhongbiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003001/003001004/003001004004/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "其它"}), f2],

    ["zfcg_huowu_zhaobiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002001/003002001001/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "货物"}), f2],
    ["zfcg_fuwu_zhaobiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002001/003002001002/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "服务"}), f2],

    ["zfcg_gongcheng_zhaobiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002001/003002001003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gctype": "工程"}), f2],

    ["zfcg_huowu_biangeng_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002002/003002002001/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "货物"}), f2],

    ["zfcg_fuwu_biangeng_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002002/003002002002/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "服务"}), f2],

    ["zfcg_huowu_zhongbiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002003/003002003001/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "货物"}), f2],

    ["zfcg_fuwu_zhongbiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002003/003002003002/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "f服务"}), f2],

    ["zfcg_gongcheng_zhongbiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002003/003002003003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gctype": "工程"}), f2],

    ["zfcg_huowu_liubiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002004/003002004001/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "货物"}), f2],

    ["zfcg_fuwu_liubiao_gg", "http://ggzyjy.yichang.gov.cn/TPFront/jyxx/003002/003002004/003002004002/", ["name", "ggstart_time", "href", "info"],
     add_info(f1, {"gctype": "f服务"}), f2],

]


def work(conp, **args):
    est_meta(conp, data, diqu="湖北省宜昌市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres","since2015","192.168.4.198","hubei","yichang"])
    for d in data:
        driver = webdriver.Chrome()
        driver.get(d[1])
        df = f1(driver, 2).values.tolist()
        for k in df[:3]:
            print(f3(driver, k[2]))
        driver.get(d[1])
        print(f2(driver))
