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
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@id='index']")
    try:
        total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'(\d+)/', total_page)[0])
    except:
        cnum = 1
    # print(cnum)
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='wb-data-item']/li[last()]//a").get_attribute('href')[-30:]
        if 'moreinfo.html' in url:
            s = '%d.html' % num if num>1 else '1.html'
            url = re.sub('moreinfo\.html', s, url)
        elif num == 1:
            url = re.sub('[0-9]+\.html', '1.html', url)
        else:
            s = '%d.html' % num if num > 1 else '1.html'
            url = re.sub('[0-9]+\.html', s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='wb-data-item']/li[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('ul', class_='wb-data-item')
    lis = table.find_all('li', class_='wb-data-list')
    data = []
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='wb-data-date').text.strip()
        ggstart_time = re.findall(r'\[(.*)\]', ggstart_time)[0]
        if 'http' in a['href']:
            href = a['href']
        else:
            href = 'http://www.ggzyzx.jl.gov.cn'+a['href']

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']= None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@id='index']")
    try:
        total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(re.findall(r'/(\d+)', total_page)[0])
    except:
        num = 1
    driver.quit()
    return num



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-article-info'][string-length()>100]")
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
    div = soup.find('div', class_='ewb-article-info').parent
    return div


data = [

    ["zfcg_zhaobiao_jz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005002/005002001/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'集中采购'}), f2],

    ["zfcg_biangeng_jz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005002/005002002/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '集中采购'}), f2],
#
    ["zfcg_zhongbiaohx_jz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005002/005002003/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '集中采购'}), f2],

    ["zfcg_zhongbiao_jz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005002/005002004/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '集中采购'}), f2],
#
    ["zfcg_liubiao_jz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005002/005002007/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '集中采购'}), f2],
#
    ["zfcg_dyly_jz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005002/005002006/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '集中采购'}), f2],
#
    ["zfcg_zhaobiao_fjz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005005/005005001/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '非集中采购'}), f2],

    ["zfcg_biangeng_fjz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005005/005005002/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '非集中采购'}), f2],

    ["zfcg_zhongbiao_fjz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005005/005005004/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '非集中采购'}), f2],

    ["zfcg_liubiao_fjz_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005005/005005006/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '非集中采购'}), f2],
#
    ["gcjs_zhaobiao_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005001/005001001/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005001/005001002/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.ggzyzx.jl.gov.cn/jyxx/005001/005001003/moreinfo.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="吉林省", **args)
    est_html(conp, f=f3, **args)


# 修改日期:2019/7/30
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_jilin_jilin"])


    # for d in data[4:]:
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


