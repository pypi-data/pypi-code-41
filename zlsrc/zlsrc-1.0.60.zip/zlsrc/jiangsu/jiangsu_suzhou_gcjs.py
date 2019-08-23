import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html,  est_meta_large


def f1(driver, num):
    locator = (By.XPATH, "//tbody[@id='ZBInfo-list']/tr[last()]/td/a | //tbody[@id='JGBAInfo-list']/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//span[@class='laypage_curr']")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())

    if num != cnum:
        val = driver.find_element_by_xpath("//tbody[@id='ZBInfo-list']/tr[last()]/td/a | //tbody[@id='JGBAInfo-list']/tr[last()]//a").get_attribute('href')[-12:]
        driver.find_element_by_xpath("//input[@id='target']").clear()
        driver.find_element_by_xpath("//input[@id='target']").send_keys(num)
        driver.find_element_by_xpath("//a[@id='skippage']").click()
        locator = (By.XPATH, "//tbody[@id='ZBInfo-list']/tr[last()]/td/a[not(contains(@href,'%s'))] | //tbody[@id='JGBAInfo-list']/tr[last()]//a[not(contains(@href,'%s'))]" % (val,val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('tbody', id='ZBInfo-list')
    if table == None:
        table = soup.find('tbody', id='JGBAInfo-list')
    trs = table.find_all('tr', recursive=False)
    url = driver.current_url
    for tr in trs:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('td')[-1].text.strip()
        if 'http://www' in a['href']:
            href = a['href']
        else:
            href = 'http://www.szjsj.gov.cn'+a['href']

        info = {}
        if 'urcInfo_zhaobiao.html' in url:
            diqu = tr.find_all('td')[1].text.strip()
            gclx = tr.find_all('td')[2].text.strip()
            zblx = tr.find_all('td')[3].text.strip()
            zgscfs = tr.find_all('td')[4].text.strip()
            info = {'diqu':diqu, 'gclx':gclx, 'zblx':zblx, 'zgscfs':zgscfs}
        elif 'urcInfo_zhongbiao.html' in url:
            diqu = tr.find_all('td')[1].text.strip()
            zblx = tr.find_all('td')[2].text.strip()
            zbdw = tr.find_all('td')[3].text.strip()
            info = {'diqu': diqu, 'zbdw': zbdw, 'zblx': zblx}
        elif 'urcInfo_jgba.html' in url:
            beian_num = tr.find_all('td')[1].text.strip()
            zljcjg = tr.find_all('td')[2].text.strip()
            info = {'beian_num': beian_num, 'zljcjg': zljcjg}
        if info:info=json.dumps(info, ensure_ascii=False)
        else:info= None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//tbody[@id='ZBInfo-list']/tr[last()]/td/a | //tbody[@id='JGBAInfo-list']/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@id='totalPages']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    num=re.findall('共<span id="totalPages"> (\d+) </span>页',driver.page_source)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    flag = 1
    if 'detailiframe' in str(driver.page_source):
        driver.switch_to_frame('detailiframe')
        flag = 2
        locator = (By.XPATH, "//table[@id='tbEdit1'][string-length()>100]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    else:
        locator = (By.XPATH, "//table[@class='TableCon'][string-length()>100]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    if flag == 1:
        div = soup.find('table', class_='TableCon').parent
    elif flag == 2:
        div = soup.find('table' ,id='tbEdit1')
    else:raise ValueError
    if div == None:raise ValueError
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.szjsj.gov.cn/zhcx/003003/003003001/003003001002/urcInfo_zhaobiao.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.szjsj.gov.cn/zhcx/003003/003003001/003003001003/urcInfo_zhongbiao.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_yanshou_gg",
     "http://www.szjsj.gov.cn/zhcx/003003/003003001/003003001010/urcInfo_jgba.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="江苏省苏州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_jiangsu_suzhou"],num=1)


    # for d in data[2:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


