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
    locator = (By.XPATH, '//div[@class="YYR1b"]//li[1]/a | //div[@class="YYR1b"]//li[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('page=(\d+)',url)[0]

    if int(cnum) != num:
        url=re.sub('(?<=page=)\d+',str(num),url)
        val = driver.find_element_by_xpath(
            '//div[@class="YYR1b"]//li[1]/a | //div[@class="YYR1b"]//li[2]/a').get_attribute('href')[-30:]

        driver.get(url)

        locator = (
            By.XPATH, '//div[@class="YYR1b"]//li[1]/a[not(contains(@href,"{val}"))] | //div[@class="YYR1b"]//li[2]/a[not(contains(@href,"{val}"))]'.format(val=val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", class_="YYR1b")

    dls = div.find_all("li")
    data = []
    for dl in dls:
        if not dl.find('a'):
            continue
        # print(dl)
        href=dl.find('a')['href']
        name=dl.find('a').get_text(strip=True)
        biaohao= dl.find('span').get_text().strip().split('\u3000')[0]
        ggstart_time = dl.find('span').get_text().strip().split('\u3000')[1]
        info=json.dumps({"biaohao":biaohao},ensure_ascii=False)
        href='http://www.gdbidding.com/'+href
        tmp = [name, ggstart_time, href,info]
        # print(tmp)

        data.append(tmp)
    df = pd.DataFrame(data=data)
    # df['info']=None
    # driver.switch_to.parent_frame()
    return df


def f2(driver):
    # global page_total
    locator = (By.XPATH, '//div[@class="YYR1b"]//li[1]/a | //div[@class="YYR1b"]//li[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    page_total=driver.find_element_by_xpath('//td[@align="right"][@valign="bottom"]').text

    page_total=re.findall('共 (\d+) 页',page_total)[0]

    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@style="margin:0px;"][string-length()>100]')
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
    div = soup.find('div', attrs={"style":"margin:0px;"})

    return div



data=[

    ["jqita_zhaobiao_gg" , 'http://www.gdbidding.com/zbxx_list.asp?id=&sys_classid=1&addtwo_ID=&addtwo=&action=&keyword=&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiao_gg" , 'http://www.gdbidding.com/zbxx_list.asp?id=&sys_classid=2&addtwo_ID=&addtwo=&action=&keyword=&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_zhongbiaohx_gg" , 'http://www.gdbidding.com/zbxx_list.asp?id=&sys_classid=4&addtwo_ID=&addtwo=&action=&keyword=&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["jqita_gqita_da_bian_gg" , 'http://www.gdbidding.com/zbxx_list.asp?id=&sys_classid=3&addtwo_ID=&addtwo=&action=&keyword=&page=1', ["name", "ggstart_time", "href", 'info'],f1, f2],

      ]


###广东元正招标采购有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "zhixiashi",
            "beijing"],
        headless=True,
        num=1,
        )
    pass