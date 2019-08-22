import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html,  est_meta


def f1(driver, num):
    locator = (By.XPATH, '//table[@width="95%"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    # locator = (By.XPATH, "//span[@class='current']")
    # snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    # cnum = int(snum)
    #
    # if num != cnum:
    #     val = driver.find_element_by_xpath("//ul[@class='comstyle newslist-01']/li[@class='content column-num1'][1]//a").get_attribute('href')[-15:]
    #     driver.execute_script('jump_57cb869c823c4ba1a3c758733e398fa9({},10);'.format(num))
    #
    #     locator = (By.XPATH, "//ul[@class='comstyle newslist-01']/li[@class='content column-num1'][1]//a[not(contains(@href,'%s'))]" % val)
    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('table', class_='kk')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('span', class_='zz1Copy')[-1].text.strip()
        ggstart_time = re.findall(r'(\d+-\d+-\d+)', ggstart_time)[0]
        onclick = a['onclick']
        tt = re.findall(r"showAnnounce\('(.*)'\)", onclick)[0].split("','")
        href = 'http://58.215.18.52:9090/homePage.action?action=showAnnounceInfo&issueRecord.prjNo='+tt[0]+'&issueRecord.prjiContPath='+tt[1]+'&announceType='+tt[2]
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    # locator = (By.XPATH, "//div[@class='number']/a[last()-2]")
    # total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    # driver.quit()
    # return int(total_page)
    return 1


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@class, 'Section')][string-length()>30]")
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
    div = soup.find('div', class_=re.compile('Section'))
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://58.215.18.52:9090/homePage.action?action=showAnnounce&announceType=cg",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://58.215.18.52:9090/homePage.action?action=showAnnounce&announceType=jg",
     ["name", "ggstart_time", "href", "info"],f1,f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省无锡市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "wuxishi"])


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 1)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


