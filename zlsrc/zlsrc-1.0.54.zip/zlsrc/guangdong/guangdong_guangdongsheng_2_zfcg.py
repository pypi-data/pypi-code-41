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
    locator = (By.XPATH, "//div[@class='pub_cont06']/div/li[last()]/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//a[@class='current']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='pub_cont06']/div/li[last()]/span/a").get_attribute('href')[-20:]
        if 'index.html' in url:
            s = 'index_%d.html'% num if num>1 else 'index.html'
            url = re.sub('index\.html', s, url)
        elif num == 1:
            re.sub('index_[0-9]+\.html', 'index.html', url)
        else:
            s = 'index_%d.html' % num if num > 1 else 'index.html'
            re.sub('index_[0-9]+\.html', s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='pub_cont06']/div/li[last()]/span/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='pub_cont06').div
    lis = table.find_all('li')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_=re.compile('span_time')).text.strip()
        if 'http' in a['href']:
            href = a['href']
        else:
            href = 'http://gpcgd.gd.gov.cn' + a['href']
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='pub_cont06']/div/li[last()]/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//a[@class='last']")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
    try:
        total_num = int(re.findall(r'index_(\d+)', total_page)[0])
    except:
        if 'index.html' in total_page:
            total_num = 1
        else:raise ValueError
    driver.quit()
    return total_num



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@class, 'detial')][string-length()>100]")
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
    div = soup.find('div', class_='pub_cont_details')
    return div


data = [
    ["zfcg_zhaobiao_pljz_gg",
     "http://gpcgd.gd.gov.cn/gpcgd/column_buy_batch/notice/index.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zblx':'批量集中采购'}), f2],

    ["zfcg_zhongbiao_pljz_gg",
     "http://gpcgd.gd.gov.cn/gpcgd/column_buy_batch/is/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'批量集中采购'}), f2],

    ["zfcg_biangeng_pljz_gg",
     "http://gpcgd.gd.gov.cn/gpcgd/column_buy_batch/edit/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'批量集中采购'}), f2],

    ["zfcg_zhaobiao_gg",
     "http://gpcgd.gd.gov.cn/gpcgd_buy_info/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://gpcgd.gd.gov.cn/gpcgd_buy_bidding_res/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_cgxxyg_gg",
     "http://gpcgd.gd.gov.cn/gpcgd_info_buy/pre/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'采购信息预告'}), f2],

    ["zfcg_biangeng_gg",
     "http://gpcgd.gd.gov.cn/gpcgd_buy_clarify/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zgys_gg",
     "http://gpcgd.gd.gov.cn/gpcgd_buy_review/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "http://gpcgd.gd.gov.cn/gpcgd_buy_bidding_candidate/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_guangdong_guangdong"])


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
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


