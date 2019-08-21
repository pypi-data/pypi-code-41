import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html, add_info



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="printSection"]')
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
    div = soup.find('div', id="printSection")

    return div


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="newsItem"]/tbody/tr[1]/td/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-60:]
    locator = (By.XPATH, '//span[@id="currentPage"]')
    cnum = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
    if int(cnum) != int(num):
        driver.execute_script("""
        goPage = function(pageNum)
            {
                var eiInfo =  _getEi();
                var perPageRecord = 10;
                var currentPage = eiInfo.get("currentPage");
                var totalPageCount = eiInfo.get("totalPageCount");
                var pageNum = pageNum;
                if((pageNum) > totalPageCount){
                    pageNum = totalPageCount;
                }
                if(pageNum < 1){
                    pageNum = 1;
                }
                changePage(perPageRecord,(pageNum - 1) * perPageRecord,pageNum);
                document.getElementById("ef_grid_result_jumpto").value=pageNum;
                }
            ;goPage(%s);""" % num)
        locator = (By.XPATH, '//table[@id="newsItem"]/tbody/tr[1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="newsItem"]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time_temp = content.xpath("./td[3]/text()")[0].strip('[').strip(']')
        ggstart_time = ggstart_time_temp[:4] +'-'+ggstart_time_temp[4:6] +'-'+ggstart_time_temp[-2:]
        url = 'http://eps.shmetro.com/portal/' + content.xpath("./td/a/@href")[0].strip().strip('.')
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//span[@id="totalPageCount"]')
    total_page = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
    driver.quit()
    return int(total_page)


data = [
    #
    ["qycg_zhaobiao_jj_gg",
     "http://eps.shmetro.com/portal/DispatchAction.do?efFormEname=PF9001&type=00&orgCode=STJT",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'竞价'}), f2],
    #
    ["qycg_zhongbiao_jj_gg",
     "http://eps.shmetro.com/portal/DispatchAction.do?efFormEname=PF9001&type=10&orgCode=STJT",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'竞价'}), f2],
    #
    ["qycg_zhaobiao_gg",
     "http://eps.shmetro.com/portal/DispatchAction.do?efFormEname=PF9001&type=20&orgCode=STJT",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["qycg_zhongbiaohx_gg",
     "http://eps.shmetro.com/portal/DispatchAction.do?efFormEname=PF9001&type=60&orgCode=STJT",
     ["name", "ggstart_time", "href", "info"], f1, f2],



    #
    ["qycg_zhongbiao_gg",
     "http://eps.shmetro.com/portal/DispatchAction.do?efFormEname=PF9001&type=30&orgCode=STJT",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["qycg_dyly_gg",
     "http://eps.shmetro.com/portal/DispatchAction.do?efFormEname=PF9001&type=40&orgCode=STJT",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["qycg_zhongbiao_1_gg",
     "http://eps.shmetro.com/portal/DispatchAction.do?efFormEname=PF9001&type=50&orgCode=STJT",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="上海地铁采购电子商务平台", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':

    for d in data:

        driver = webdriver.Chrome()
        url = d[1]
        driver.get(url)
        df = f1(driver, 2)
        #
        for u in df.values.tolist()[:1]:
            print(f3(driver, u[2]))
        driver.get(url)

        print(f2(driver))
    # work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "bc_eps_shmetro_com"])
    # driver = webdriver.Chrome()
    # driver.get("http://ggzy.ah.gov.cn/login.do?method=beginlogin")
    # print(f2(driver))
