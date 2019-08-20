import random
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large




def f1(driver, num):
    locator = (By.XPATH, "//div[@class='zhbdl_list']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//div[@class='next']")
    page = WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(re.findall(r'(\d+)/', page)[0])

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='zhbdl_list']/ul/li[last()]/a").get_attribute('href')[-12:]
        url = re.sub(r'page=[0-9]+', 'page=%d' % num, driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='zhbdl_list']/ul/li[last()]/a[not(contains(@href,'{}'))]".format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', class_='zhbdl_list').ul
    lis = table.find_all('li')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()

        ggstart_time = tr.find('span').text.strip('[]')

        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.fecc.cc/' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='zhbdl_list']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='next']")
    page = WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)页', page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='list-show'][string-length()>50]")
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
    div = soup.find('div', class_='list-show')
    if div == None:
        raise ValueError
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=1&M=1&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=1&M=2&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=1&M=3&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=2&M=4&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_bu_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=2&M=5&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=2&M=6&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ####
    ["jqita_zhaobiao_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=3&M=7&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'投融资招标'}), f2],

    ["jqita_gqita_bian_bu_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=3&M=8&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'投融资招标'}), f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.fecc.cc/zhbdllist.asp?B=3&M=9&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'投融资招标'}), f2],
]


# 福建省闽咨集团
def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "fujian_fujiansheng_daili"], )


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


