import json
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
from zlsrc.util.etl import est_html, est_meta, add_info




def f1(driver, num):
    locator = (By.XPATH, "//td[@height='574']/table[last()]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@id='AspNetPager1']/span")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//td[@height='574']/table[last()]//a").get_attribute('href')[-30:]

        driver.execute_script("javascript:__doPostBack('AspNetPager1','{}')".format(num))
        locator = (By.XPATH, "//td[@height='574']/table[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('td', height='574')
    lis = div.find_all('table', recursive=False)
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('td')[-1].text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.nmgzbw.com/' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df




def f2(driver):
    locator = (By.XPATH, "//td[@height='574']/table[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    num = driver.find_element_by_xpath("//div[@id='AspNetPager1']/a[last()-2]").text.strip()

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@class='p14hui'][string-length()>30]")
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
    # div = soup.find('td', class_='p14hui').parent('table')[0].parent('table')
    div = soup.find('table', attrs={'style':'margin-top:20px','width':'700'})
    if not div:
        raise ValueError
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=7ddb93dc-b88f-4b7d-b7cc-6fe514950cb0&oty=zbggx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=6940dc0c-c610-41b6-b824-fc424f28e7be&oty=zbggx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gjzb_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=05778c4c-0055-4c33-89e4-7585fcabd791&oty=zbggx",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'国际招标'}), f2],

    ["jqita_zhaobiao_zytz_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=a9c8c3f4-5563-40e9-b02f-eacd242f6912&oty=zbggx",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '中央投资'}), f2],

    ["yiliao_zhaobiao_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=53393106-5af5-494f-ba31-a598cef77989&oty=zbggx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=8417ba5f-bc27-4849-95bb-7dac3e282da0&oty=zbggx",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #######

    ["gcjs_zhongbiao_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=36bd5498-9a20-4e21-ad3a-ab6cd4abbffe&oty=zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=b19a12b1-a4c3-478f-8d52-d34e006318fb&oty=zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gjzb_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=fa1ccbfb-4860-4ab2-ab8f-fb5aeee9b685&oty=zbgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '国际招标'}), f2],

    ["jqita_zhongbiao_zytz_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=43a22b6b-1ede-47ca-b616-c70d9a708432&oty=zbgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '中央投资'}), f2],

    ["yiliao_zhongbiao_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=ea0938a5-708e-4ba3-a731-43e254360c94&oty=zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://www.nmgzbw.com/NewsList.aspx?oid=79a5bf78-195e-4d13-a66f-90db73575a5a&oty=zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

# 内蒙古存信招标有限责任公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="内蒙古自治区", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest", "neimenggu_neimenggusheng_daili"],add_ip_flag=True)


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #
    #     print(url)
        # driver.get(url)
        # df = f2(driver)
        # print(df)
        # driver = webdriver.Chrome()
        # driver.get(url)
        #
        # df=f1(driver, 3)
        # print(df.values)
        # for f in df[2].values:
        #     d = f3(driver, f)
        #     print(d)



