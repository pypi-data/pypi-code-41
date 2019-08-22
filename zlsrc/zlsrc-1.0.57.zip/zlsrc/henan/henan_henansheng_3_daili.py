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
    locator = (By.XPATH, '//div[@class="cwzzw"]')
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
    div = soup.find('div', class_="cwzzw")

    return div


def f1(driver, num):


    locator = (By.XPATH, '//div[@class="zbox"]/ul/li[1]/a')
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
    locator = (By.XPATH, '//span[@id="ShowChangeInfo"]')
    txt = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
    cnum = re.findall('(\d+)\/',txt)[0]
    if int(cnum) != int(num):
        driver.execute_script("goToPage(%s);"%num)
        locator = (By.XPATH, '//div[@class="zbox"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="zbox"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = 'http://www.hnzbcg.com.cn' + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] =None
    return df


def f2(driver):

    locator = (By.XPATH, '//span[@id="ShowChangeInfo"]')
    txt = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)',txt)[0]
    driver.quit()
    return int(total_page)




data = [
    #
    ["jqita_zhaobiao_gg",
     "http://www.hnzbcg.com.cn/zbinfo/node_16.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["jqita_zhaobiao_2_gg",
     "http://www.hnzbcg.com.cn/zbinfo/node_15.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["jqita_biangeng_gg",
     "http://www.hnzbcg.com.cn/zbinfo/node_14.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["jqita_zhongbiao_gg",
     "http://www.hnzbcg.com.cn/zbinfo/node_13.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

##河南招标采购服务有限公司
def work(conp, **arg):
    est_meta(conp, data=data, diqu="河南省", **arg)
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
    #         f3(driver, u[2])
    #     driver.get(url)
    #
    #     print(f2(driver))
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_hnzbcg_com_cn"])
    # driver = webdriver.Chrome()
    # driver.get("http://ggzy.ah.gov.cn/login.do?method=beginlogin")
    # print(f2(driver))