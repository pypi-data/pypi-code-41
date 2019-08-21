import json
import random
from math import ceil
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large


def f1(driver, num):
    locator = (By.XPATH, "//div[@id='palist']/div[last()]//div[@class='left']/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//li[contains(@class, 'pgCurrent')]")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@id='palist']/div[last()]//div[@class='left']/a").get_attribute('href')[-30:]
        if num < cnum:
            for i in range(cnum-num):
                locator = (By.XPATH, "//ul[@class='pages']/li")
                txts = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
                flag = 0
                for tx in txts:
                    t = tx.text.strip()
                    if t == '%d'% num:
                        driver.find_element_by_xpath("//ul[@class='pages']/li[string()='{}']".format(t)).click()
                        locator = (By.XPATH, "//li[contains(@class, 'pgCurrent')][string()='{}']".format(num))
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                        flag = 1
                        break
                if flag == 1: break
                val = driver.find_element_by_xpath("//div[@id='palist']/div[last()]//div[@class='left']/a").get_attribute('href')[-60:]

                driver.find_element_by_xpath("//li[@class='page-number'][1]").click()
                locator = (By.XPATH, "//div[@id='palist']/div[last()]//div[@class='left']/a[not(contains(@href, '{}'))]".format(val))
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        if num > cnum:
            for i in range(num-cnum):
                locator = (By.XPATH, "//ul[@class='pages']/li")
                txts = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
                flag = 0
                for tx in txts:
                    t = tx.text.strip()
                    if t == '%d'% num:
                        driver.find_element_by_xpath("//ul[@class='pages']/li[string()='{}']".format(t)).click()
                        locator = (By.XPATH, "//li[contains(@class, 'pgCurrent')][string()='{}']".format(num))
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                        flag = 1
                        break
                if flag == 1: break
                val = driver.find_element_by_xpath("//div[@id='palist']/div[last()]//div[@class='left']/a").get_attribute('href')[-60:]

                driver.find_element_by_xpath("//li[@class='page-number'][last()]").click()
                locator = (By.XPATH, "//div[@id='palist']/div[last()]//div[@class='left']/a[not(contains(@href, '{}'))]".format(val))
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//li[contains(@class, 'pgCurrent')]")
        tnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())
        if tnum != num:
            raise ValueError

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', id='palist')
    lis = div.find_all('div', recursive=False)
    url = driver.current_url
    for tr in lis:
        a = tr.find('a', class_='title')
        try:
            name = a['title']
        except:
            name = a.text.strip()

        if 'http' in a['href']:
            href = a['href']
        else:
            href = 'http://bid.fujianbid.com' + a['href']

        if 'filesList.shtml' in url:
            try:
                ggstart_time = tr.find_all('div', class_='col')[-2].extract().span.text.strip()
            except:
                ggstart_time = "-"
        else:
            try:
                ggstart_time = tr.find_all('div', class_='col')[-5].extract().span.text.strip()
            except:
                ggstart_time = "-"

        info = {}
        zbdl = tr.find('div', class_='row').span
        if zbdl:
            zbdl = zbdl.text.strip()
            if zbdl: info['zbdl'] = zbdl
        ts = tr.find_all('div', class_='col')
        if 'filesList.shtml' in url:
            if ts[0].span:
                xmlx = ts[0].span.text.strip()
                if xmlx:info['xmlx']=xmlx
            if ts[-1].span:
                end_time = ts[-1].span.text.strip()
                if end_time:info['end_time']=end_time
        else:
            if ts[0].span:
                xmlx = ts[0].span.text.strip()
                if xmlx:info['xmlx']=xmlx
            if ts[1].span:
                bsend_time = ts[1].span.text.strip()
                if bsend_time:info['bsend_time']=bsend_time
            if ts[2].span:
                zblx = ts[2].span.text.strip()
                if zblx:info['zblx']=zblx
            if ts[3].span:
                dyend_time = ts[3].span.text.strip()
                if dyend_time:info['dyend_time']=dyend_time
            if ts[4].span:
                kblx = ts[4].span.text.strip()
                if kblx: info['kblx'] = kblx
            if ts[5].span:
                kbdd = ts[5].span.text.strip()
                if kbdd: info['kbdd'] = kbdd
            if ts[6].span:
                tbend_time = ts[6].span.text.strip()
                if tbend_time: info['tbend_time'] = tbend_time
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@id='palist']/div[last()]//div[@class='left']/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@class='itemnum']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    tnum = re.findall(r'\d+', total_page)[0]
    num = ceil(int(tnum)/10)

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content' and contains(@style, 'block')][string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.5)
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
    div=soup.find('div', class_='content-sec')
    if div == None:raise ValueError
    return div


data = [

    ["jqita_zhaobiao_gg",
     "http://bid.fujianbid.com/flow_page!projectBulletinList.shtml?type=normalBulletin&bulletinType=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["jqita_gqita_bian_bu_gg",
     "http://bid.fujianbid.com/flow_page!projectBulletinList.shtml?type=addedBulletin&bulletinType=1",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_zhongbiao_gg",
     "http://bid.fujianbid.com/flow_page!filesList.shtml?bulletinType=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_lx1_gg",
     "http://bid.fujianbid.com/flow_page!projectBulletinList.shtml?type=normalBulletin&bulletinType=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_lx1_gg",
     "http://bid.fujianbid.com/flow_page!filesList.shtml?bulletinType=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bian_bu_lx1_gg",
     "http://bid.fujianbid.com/flow_page!projectBulletinList.shtml?type=addedBulletin&bulletinType=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

###福易采电子交易平台
def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "bid_fujianbid_com"])


    # for d in data[1:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 12)
    #     print(df.values)
        # for f in df[2].values:
        #     d = f3(driver, f)
        #     print(d)


