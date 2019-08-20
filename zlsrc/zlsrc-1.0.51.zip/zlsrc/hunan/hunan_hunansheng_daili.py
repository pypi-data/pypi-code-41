import pandas as pd
import re
from lxml import etree
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html, add_info




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="m-bd"]')
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
    div = soup.find('div', class_="m-bd")

    return div


def f1(driver, num):


    locator = (By.XPATH, '//div[@class="lb-link"]/ul/li[1]/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
    locator = (By.XPATH, '//div[@class="pagination"]/div/div/em[1]')
    cnum = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text

    if int(cnum) != int(num):
        new_url = re.sub("index[_\d]*",'index_'+str(num),driver.current_url)
        driver.get(new_url)
        locator = (By.XPATH, '//div[@class="lb-link"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="lb-link"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        ggstart_time = content.xpath("./a/span[3]/text()")[0].strip()
        url =  content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] =None
    return df


def f2(driver):

    locator = (By.XPATH, '//div[@class="pagination"]/div/div/em[2]')
    total_page = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
    driver.quit()
    return int(total_page)




data = [
    #
    ["jqita_zhaobiao_gg",
     "http://www.hnbidding.com/zbgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["jqita_biangeng_gg",
     "http://www.hnbidding.com/bggg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["jqita_gqita_ps_gg",
     "http://www.hnbidding.com/psjggs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"评审结果公示"}), f2],

    #
    ["jqita_zhongbiaohx_hw_gg",
     "http://www.hnbidding.com/zbhw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"货物"}), f2],
    #
    ["jqita_zhongbiaohx_gc_gg",
     "http://www.hnbidding.com/zbgc/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"工程"}), f2],
    #
    ["jqita_zhongbiaohx_fw_gg",
     "http://www.hnbidding.com/fwzb/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"服务"}), f2],
    #
    ["jqita_zhongbiao_hw_gg",
     "http://www.hnbidding.com/bghw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"货物"}), f2],
    #
    ["jqita_zhongbiao_gc_gg",
     "http://www.hnbidding.com/bggc/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"工程"}), f2],
    #
    ["jqita_zhongbiao_fw_gg",
     "http://www.hnbidding.com/bgfw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"服务"}), f2],


]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="湖南省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    #
    # for d in data:
    #
    #     driver = webdriver.Chrome()
    #     url = d[1]
    #     driver.get(url)
    #     df = f1(driver, 2)
    #     #
    #     for u in df.values.tolist()[:1]:
    #         print(f3(driver, u[2]))
    #     driver.get(url)
    #
    #     print(f2(driver))
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_hnzbcg_com_cn"])
    # driver = webdriver.Chrome()
    # driver.get("http://ggzy.ah.gov.cn/login.do?method=beginlogin")
    # print(f2(driver))