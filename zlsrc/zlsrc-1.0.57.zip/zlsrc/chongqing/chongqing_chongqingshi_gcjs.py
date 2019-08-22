import json


import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zlsrc.util.etl import  est_meta, est_html, add_info, est_gg



def f1(driver, num):
    locator = (By.XPATH, '//table[@id="dgData"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//span[@id="lblCurrentIndex"]//font').text

    if int(cnum) != num:

        while True:
            cnum = int(driver.find_element_by_xpath('//span[@id="lblCurrentIndex"]//font').text)
            val = driver.find_element_by_xpath('//table[@id="dgData"]//tr[2]//a').get_attribute('href')[-45:]

            if cnum > num:
                if cnum - num > page_total//2:
                    driver.execute_script("javascript:__doPostBack('btnFirst','')")
                else:
                    driver.execute_script("javascript:__doPostBack('Linkbutton2','')")

            elif cnum < num :
                if num - cnum > page_total//2:
                    driver.execute_script("javascript:__doPostBack('btnLast','')")
                else:
                    driver.execute_script("javascript:__doPostBack('Linkbutton3','')")
            else:
                break

            locator = (
                By.XPATH, "//table[@id='dgData']//tr[2]//a[not(contains(@href,'{}'))]".format(val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", id="dgData")
    dls = div.find_all("tr")[1:]

    data = []
    for dl in dls:
        tds = dl.find_all('td')
        name=dl.find('a').get_text(strip=True)
        href=dl.find('a')['href']
        mark=div.find('tr').find_all('td')[1].get_text()
        ggstart_time = tds[-1].get_text().strip()


        if '中标' in mark:
            diqu = tds[-2].get_text(strip=True)
            dw=tds[1].get_text(strip=True)
            info = json.dumps({"diqu": diqu,"dw":dw}, ensure_ascii=False)
        elif "地区" in mark:
            diqu = tds[-2].get_text(strip=True)
            info = json.dumps({"diqu": diqu}, ensure_ascii=False)

        else:
            info=None

        if 'http' in href:
            href = href
        else:
            href = 'http://www.cqjsxx.com/webcqjg/GcxxFolder/' + href

        tmp = [name, ggstart_time, href,info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f4(driver, num):
    locator = (By.XPATH, '//table[@id="dgFileNotice"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//span[@id="Pager1_CPage"]').text

    if int(cnum) != num:

        while True:
            cnum = int(driver.find_element_by_xpath('//span[@id="Pager1_CPage"]').text)
            val = driver.find_element_by_xpath('//table[@id="dgFileNotice"]//tr[2]//a').get_attribute('href')[-45:]

            if cnum > num:
                if cnum - num > page_total//2:
                    driver.execute_script("javascript:__doPostBack('Pager1$LB_First','')")
                else:
                    driver.execute_script("javascript:__doPostBack('Pager1$LB_Back','')")

            elif cnum < num :
                if num - cnum > page_total//2:
                    driver.execute_script("javascript:__doPostBack('Pager1$LB_Last','')")
                else:
                    driver.execute_script("javascript:__doPostBack('Pager1$LB_Next','')")
            else:
                break

            locator = (
                By.XPATH, "//table[@id='dgFileNotice']//tr[2]//a[not(contains(@href,'{}'))]".format(val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("table", id="dgFileNotice")
    dls = div.find_all("tr")[1:]

    data = []
    for dl in dls:
        tds = dl.find_all('td')
        name=dl.find('a').get_text(strip=True)
        href=dl.find('a')['href']
        ggstart_time = tds[-1].get_text().strip()

        driver.execute_script(href)
        windows_handle=driver.window_handles
        driver.switch_to.window(windows_handle[1])
        WebDriverWait(driver, 10).until(lambda driver:"www.cqjsxx.com" in  driver.current_url)
        href=driver.current_url
        driver.close()
        driver.switch_to.window(windows_handle[0])

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    global page_total
    locator = (By.XPATH, '//table[@id="dgData"]//tr[2]//a |//table[@id="dgFileNotice"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page_total=int(driver.find_element_by_xpath('//span[@id="lblPageCount"]//font |//span[@id="Pager1_Pages"]').text)

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="PNInfo"][string-length()>50]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='PRight')

    return div



data=[

["gcjs_zhaobiao_gg" , 'http://www.cqjsxx.com/webcqjg/GcxxFolder/notice.aspx', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_zhongbiaohx_gg" , 'http://www.cqjsxx.com/webcqjg/GcxxFolder/zhongbiao.aspx', ["name", "ggstart_time", "href", 'info'],f1, f2],
["gcjs_yanshou_gg" , 'http://www.cqjsxx.com/webcqjg/GcxxFolder/jgysba_list.aspx', ["name", "ggstart_time", "href", 'info'],f4, f2],

      ]


##重庆建设工程信息网
def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=False,
        num=1,ipNum=0,image_show_gg=2
        )
    pass
