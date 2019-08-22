import re
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time




def f1(driver, num):

    locator = (By.XPATH, '//a[@class="on"]')
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    locator = (By.XPATH, '//div[@class="ny_news_list"]/ul/li[1]/div[3]/h3/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-5:]

    if int(cnum) != int(num):
        new_url = re.sub('page=\d+','page='+str(num),driver.current_url)
        driver.get(new_url)

        locator = (By.XPATH, '//div[@class="ny_news_list"]/ul/li[1]/div[3]/h3/a[not(contains(@href,"%s"))]'%(val))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="ny_news_list"]/ul/li')

    data = []
    for content in content_list:

        name = content.xpath("./div[3]/h3/a/@title")[0].strip()

        url = 'http://www.cntec.com.cn/' + content.xpath("./div[3]/h3/a/@href")[0].strip()

        ggstart_time = content.xpath("./div[2]/div[3]/text()")[0].strip() +'-'+ content.xpath("./div[2]/div[2]/text()")[0].strip().replace('月','-') + content.xpath("./div[2]/div[1]/text()")[0].strip()

        temp = [name, ggstart_time, url]

        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    locator = (By.XPATH, '//span[@class="num"]/a[last()]')
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='news_xq']")
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
    soup = BeautifulSoup(page, 'html.parser')
    div=soup.find('div',class_='news_xq')
    return div


data = [
    ["qycg_zhaobiao_gg",
     "http://www.cntec.com.cn/list.php?pid=2&ty=14&page=100000",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]




def work(conp, **args):
    est_meta(conp, data=data, diqu="中国乡镇企业有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest1", "www_cntec_com_cn"]

    work(conp)
    # driver = webdriver.Chrome()
    # driver.get('http://www.cntec.com.cn/list.php?pid=2&ty=14&page=100000')
    # print(f2(driver))
    # f1(driver,32)
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     df_list = f1(driver, i).values.tolist()
    #     print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
