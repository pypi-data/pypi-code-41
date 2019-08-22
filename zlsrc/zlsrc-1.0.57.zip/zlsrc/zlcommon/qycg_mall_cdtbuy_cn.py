import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large



def f1(driver, num):
    locator = (By.XPATH, "//ul[@id='tenderBull']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall(r'page=(\d+)', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@id='tenderBull']/li[last()]/a").get_attribute('onclick').split("'")[1]
        url = re.sub('page=[0-9]+', 'page=%d' % num, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@id='tenderBull']/li[last()]/a[not(contains(@onclick,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', id='tenderBull')
    lis = div.find_all('li')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span').text.strip()
        link = a['onclick'].split("'")[1]
        if 'http' in link:
            href = link
        else:
            href = 'http://mall.cdtbuy.cn/LoginControllerCgjy.do?method=showResultBulletinInquiryView&objId=' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='pDiv']/div/span/span")
    num = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//span[@id='bulletincontents'][string-length()>40]")
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
    div = soup.find('span', id='bulletincontents')
    return div


data = [

    ["qycg_zhaobiao_gg",
     "http://mall.cdtbuy.cn/LoginControllerCgjy.do?method=getMoreTenderBulletinPage&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'网上竞价'}),f2],

    ["qycg_zhongbiao_gg",
     "http://mall.cdtbuy.cn/LoginControllerCgjy.do?method=getMoreResultBulletinPage&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'网上竞价'}), f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="大唐集团公司电子商城", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "mall_cdtbuy_cn"])


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
    #     df=f1(driver, 12)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


