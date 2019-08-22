import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import est_tbs, est_meta, est_html


def f1(driver, num):
    locator = (By.XPATH, '//tbody/tr[@role="row"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//li[@class="paginate_button active"]/a').text

    if int(cnum) != int(num):

        while True:
            val = driver.find_element_by_xpath('//tbody/tr[@role="row"][1]//a').get_attribute('onclick')
            cnum=int(driver.find_element_by_xpath('//li[@class="paginate_button active"]/a').text)
            if cnum < num:
                click_button = driver.find_element_by_xpath('//li[@id="psmsdatalist_next"]/a')
                driver.execute_script("arguments[0].click()", click_button)
            elif cnum > num:
                click_button = driver.find_element_by_xpath('//li[@id="psmsdatalist_first"]/a')
                driver.execute_script("arguments[0].click()", click_button)
            else:
                break

            # 第二个等待
            locator = (By.XPATH, "//tbody/tr[@role='row'][1]//a[not(contains(@onclick,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('tr', role='row')[:-1]

    for tr in lis:
        href=tr.find('a')['onclick']
        name=tr.find('a')['title']
        ggstart_time=tr.find('span',class_="time over").get_text().strip('发布')
        publish_id=re.findall('showDetail\(".+?","(.*?)",".*?"\);',href)[0]
        id_=re.findall('showDetail\(".+?",".*?","(.*?)"\);',href)[0]

        if (publish_id == "null") or (not publish_id):
            href="http://zbb.nankai.edu.cn"+"e?page=cms.cgtext&id="+id_
        else:
            href="http://zbb.nankai.edu.cn"+"/provider/#/publish/"+publish_id

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def f2(driver):
    locator = (By.XPATH, '//tbody/tr[@role="row"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//ul[@class="pagination"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    val=driver.find_element_by_xpath('//tbody/tr[@role="row"][1]//a').get_attribute('onclick')

    driver.find_element_by_xpath('//ul[@class="pagination"]/li[@id="psmsdatalist_last"]/a').click()

    locator = (By.XPATH, "//tbody/tr[@role='row'][1]//a[not(contains(@onclick,'%s'))]" % val)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//li[@class="paginate_button active"]/a').text

    driver.quit()
    return int(total)


def f3(driver, url):

    driver.get(url)

    locator = (By.XPATH, '//iframe[@id="contentFrame"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    driver.switch_to.frame('contentFrame')
    locator = (By.XPATH, '//iframe[@id="content_frame"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    driver.switch_to.frame('content_frame')
    locator = (By.XPATH, '//div[@id="viewerContainer"][string-length()>100]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    before = len(driver.page_source)
    time.sleep(1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.5)
        after = len(driver.page_source)
        i += 1
        if i > 5: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div1 = soup.find('div', id="viewerContainer")

    driver.switch_to.default_content()
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div2=soup.find(id='contentFrame').find_previous_sibling('div')
    div = BeautifulSoup(str(div2)+str(div1),'html.parser')

    if div == None:
        raise ValueError('div is None')


    return div



data = [

    ["qycg_zhaobiao_gg", "http://zbb.nankai.edu.cn/sfw_cms/e?page=cms.psms.gglist&typeDetail=A",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_gg", "http://zbb.nankai.edu.cn/sfw_cms/e?page=cms.psms.gglist&typeDetail=B",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]




# pprint(data)



def work(conp, **args):
    est_meta(conp, data=data, diqu="南开大学招投标管理办公室", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "lchest", "hubei_zhijiang"], total=2, headless=False, num=1)
    pass
    driver=webdriver.Chrome()
    # driver.switch_to.default_content()
    f3(driver,'http://zbb.nankai.edu.cn/provider/#/publish/16BDF5B566622A916FCC4F2579667622')


