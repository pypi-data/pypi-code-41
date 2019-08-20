import re
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time



def f1(driver, num):
    locator = (By.XPATH, '//font[@class="fystyle"][last()]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('第(\d+)页', txt)[0]
    locator = (By.XPATH, '//table[@align="left"]/tbody/tr[@align="left"][1]/td/a')
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')[-15:]

    if int(cnum) != int(num):
        new_url = re.sub('index[_\d]*', 'index_' + str(num-1), driver.current_url)

        driver.get(new_url)

        locator = (By.XPATH, '//table[@align="left"]/tbody/tr[@align="left"][1]/td/a[not(contains(@href,"%s"))]' % (val))

        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@align="left"]/tbody/tr[@align="left"]')

    data = []
    for content in content_list:
        name = content.xpath("./td/a/@title")[0].strip()

        url = driver.current_url.rsplit('/',1)[0] + content.xpath("./td/a/@href")[0].strip('.')

        ggstart_time = content.xpath("./td[4]/text()")[0].strip()

        temp = [name, ggstart_time, url]

        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//font[@class="fystyle"][last()-1]')
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('总共(\d+)页',txt)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@width="99%"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('table', width='99%')
    return div


data = [
    ["gcjs_zhaobiao_jxssj_gg",
     "http://www.jxtb.org.cn/zbgg/jxssj/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'江西省省级'}), f2],
    ["gcjs_zhaobiao_jjs_gg",
     "http://www.jxtb.org.cn/zbgg/jjs/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '九江市'}), f2],
    ["gcjs_zhaobiao_jdzs_gg",
     "http://www.jxtb.org.cn/zbgg/jdzs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '景德镇市'}), f2],
    ["gcjs_zhaobiao_pxs_gg",
     "http://www.jxtb.org.cn/zbgg/pxs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '萍乡市'}), f2],
    ["gcjs_zhaobiao_yts_gg",
     "http://www.jxtb.org.cn/zbgg/yts/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '鹰潭市'}), f2],
    ["gcjs_zhaobiao_ycs_gg",
     "http://www.jxtb.org.cn/zbgg/ycs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '宜春市'}), f2],
    ["gcjs_zhaobiao_jas_gg",
     "http://www.jxtb.org.cn/zbgg/jas/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '吉安市'}), f2],
    ["gcjs_zhaobiao_fzs_gg",
     "http://www.jxtb.org.cn/zbgg/fzs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '抚州市'}), f2],





    ["gcjs_zhongbiaohx_gg",
     "http://www.jxtb.org.cn/zbhxrgs2/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.jxtb.org.cn/zbjg/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlest", "www_jxtb_org_cn"]
    # driver=webdriver.Chrome()
    # driver.get('http://bulletin.sntba.com/xxfbcmses/search/change.html?searchDate=1994-07-17&dates=300&categoryId=92&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=&word=&page=2')
    # print(f1(driver, 3).values.tolist())
    work(conp,pageloadstrategy='none',pageloadtimeout=120)
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
    #     # print(df_list[:10])
    #     df1 = random.choice(df_list)
    #     print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
