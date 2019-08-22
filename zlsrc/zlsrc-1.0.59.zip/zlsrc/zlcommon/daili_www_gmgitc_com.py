import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, est_meta, add_info



def f1(driver, num):
    locator = (By.XPATH, '//pre[string-length()>100]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum=re.findall('thisPage=(\d+)',url)[0]

    if num != int(cnum):
        page_count=len(driver.page_source)
        url=re.sub('(?<=thisPage=)\d+',str(num),url)
        driver.get(url)
        WebDriverWait(driver,20).until(lambda driver:len(driver.page_source) != page_count and len(driver.page_source)>200)

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("pre").get_text()
    contents=json.loads(div,encoding='utf8')['data']

    data = []
    for c in contents:

        title=c.get('Title')
        if not title:
            title=c.get('PrjName')

        ggstart_time=c.get('ShowDate')
        hrefid=c.get('SNID').strip()
        if hrefid:
            href='http://www.gmgitc.com/Bid/BidInfoDetail?SNID=%s'%hrefid
        else:
            hrefid=c.get('ID').strip()

            sncode=c.get('SNCode')

            if sncode:
                href='http://www.gmgitc.com/Bid/ClarifyDetail?ID={ID}&tempid={tempid}'.format(ID=hrefid,tempid=sncode)
            else:
                href='http://www.gmgitc.com/Bid/BidResultDetail?ID=%s'%hrefid

        code = c.get("Code")
        if code:
            info=json.dumps({"code":code},ensure_ascii=False)
        else:
            info=None
        tmp = [title, ggstart_time, href,info]
        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df



def f2(driver):
    locator = (By.XPATH, '//pre[string-length()>50]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    num=re.findall('"TotalPages":(\d+)',driver.page_source)[0]

    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//article[@class="info"][string-length()>200]')
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
    div=soup.find('div',class_='RichInfo006')

    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.gmgitc.com/Handlers/Default/Notice_BidInfo_List.ashx?categoryA=%E5%9B%BD%E9%99%85%E5%9B%BD%E5%86%85&categoryB=%E7%AE%A1%E8%BE%96%E9%83%A8%E9%97%A8&categoryC=%E8%A1%8C%E4%B8%9A%E5%88%86%E7%B1%BB&keyWord=&thisPage=1&rowsEachPage=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.gmgitc.com/Handlers/Default/Notice_BidResult_List.ashx?categoryA=%E5%9B%BD%E9%99%85%E5%9B%BD%E5%86%85&categoryB=%E7%AE%A1%E8%BE%96%E9%83%A8%E9%97%A8&categoryC=%E8%A1%8C%E4%B8%9A%E5%88%86%E7%B1%BB&keyWord=&thisPage=1&rowsEachPage=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_biangeng_gg",
     "http://www.gmgitc.com/Handlers/Default/Notice_Clarify_List.ashx?categoryA=%E5%9B%BD%E9%99%85%E5%9B%BD%E5%86%85&categoryB=%E7%AE%A1%E8%BE%96%E9%83%A8%E9%97%A8&categoryC=%E8%A1%8C%E4%B8%9A%E5%88%86%E7%B1%BB&keyWord=&thisPage=2&rowsEachPage=15",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

##国义招标股份有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="国义招标", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_gmgitc_com"],num=1,ipNum=0)

    # driver = webdriver.Chrome()
    # url = "http://www.gmgitc.com/Notice/BidInfo/List.aspx"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.gmgitc.com/Notice/BidInfo/List.aspx"
    # driver.get(url)
    # for i in range(31, 33):
    #     df=f1(driver, i)
    #     print(df.values)
