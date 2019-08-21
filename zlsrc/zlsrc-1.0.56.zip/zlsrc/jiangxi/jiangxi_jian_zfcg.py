import time

import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlsrc.util.etl import est_meta, est_html


def f1(driver,num):
    locator = (By.XPATH, '//div[@class="publicList bgwhite pagingList"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath("//a[@class='curpage']").text)
    url=driver.current_url
    if num != cnum:
        if num ==1:
            url=re.sub('index_\d+.html','index.html',url)
        else:
            url=re.sub('index_*\d*.html','index_%s.html'%(num-1),url)
        val = driver.find_element_by_xpath('//div[@class="publicList bgwhite pagingList"]//li[1]/a').get_attribute('href').rsplit(
            '/', maxsplit=1)[1]

        driver.get(url)

        locator = (By.XPATH, '//div[@class="publicList bgwhite pagingList"]//li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    div = soup.find('div', class_="publicList bgwhite pagingList")
    uls = div.find_all('li')

    data = []
    for li in uls:
        name = li.a['title']
        href = li.a['href'].strip('..')
        if 'http' in href:
            href=href
        else:
            href='http://www.jazfcg.com.cn/cgxx'+href
        ggstart_time = li.span.get_text()
        tmp = [name, ggstart_time, href]
        # print(tmp)
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="publicList bgwhite pagingList"]//li[1]/a')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@id="div_page"]/a[last()]').get_attribute('href')
    total = re.findall('index_(\d+).html', total)[0]

    driver.quit()
    return int(total)+1

def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//div[@class="publicList bgwhite pagingList"]//li[1]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        column_list=['采购公告','变更公告','答疑澄清','结果公示','单一来源公示']

        global column_mark
        column_mark=column_list[num-1]

        url=driver.current_url
        if 'www.jazfcg.com.cn' in url:
            val=driver.find_element_by_xpath('//div[@id="div_page"]/a[last()]').get_attribute('href')
            se=Select(driver.find_element_by_xpath('//select[@id="searchColumn"]'))
            se.select_by_index(num)
            time.sleep(0.1)
            driver.find_element_by_xpath('//div[@class="fl intsub searchBtn"]').click()
            locator=(By.XPATH,'//div[@id="div_page"]/a[last()][not(contains(@href,"%s"))]'%val)
            WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
            time.sleep(10)
        return f(*args)
    return inner




def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, '//div[@class="textmid"][string-length()>10]')
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
    div = soup.find('div',class_="textshow")
    if '有效期失效不能访问' in str(div):
        raise ValueError
    return div



data=[

    ["zfcg_zhaobiao_gg","http://www.jazfcg.com.cn/cgxx/cggg/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_biangeng_gg","http://www.jazfcg.com.cn/cgxx/bggg/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://www.jazfcg.com.cn/cgxx/dycq/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.jazfcg.com.cn/cgxx/jggs/index.html",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_dyly_gg","http://www.jazfcg.com.cn/cgxx/dylygs/index.html",["name","ggstart_time","href",'info'],f1,f2],
    

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省吉安市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':
    #
    conp=["postgres","since2015","192.168.3.171","lch","jiangxi_jian"]

    work(conp=conp,headless=False,num=1)
    #
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://www.jazfcg.com.cn/cgxx/jgssfz/jggs/201901/t20190102_2574457.html')
    # print(df)