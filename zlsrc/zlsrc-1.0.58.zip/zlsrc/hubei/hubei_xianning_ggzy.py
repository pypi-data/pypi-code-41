import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large


def f1(driver, num):
    locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//td[@class='yahei redfont']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@cellspacing='3']/tbody/tr[last()]//a").get_attribute('href')[-30:]
        url = re.sub('Paging=[0-9]+','Paging=%d'%num, url)
        driver.get(url)
        locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', cellspacing='3').tbody
    lis = table.find_all('tr', height="25")
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('font')[-1].text.strip()
        href = 'http://xnztb.xianning.gov.cn'+a['href']
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', total_page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[contains(@id, 'TDContent')][string-length()>200]")
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
    div = soup.find('table', id=re.compile('^tblInfo'))
    return div


data = [
    ["gcjs_zhaobiao_fw_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005001/005001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'房屋建筑与基础设施工程'}),f2],

    ["gcjs_gqita_bian_cheng_fw_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005001/005001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gclx':'房屋建筑与基础设施工程'}),f2],

    ["gcjs_zhongbiaohx_fw_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005001/005001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '房屋建筑与基础设施工程'}), f2],

    ["gcjs_zhongbiao_fw_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005001/005001004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '房屋建筑与基础设施工程'}), f2],
    ####
    ["gcjs_zhaobiao_jt_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005002/005002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '交通工程'}), f2],

    ["gcjs_gqita_bian_cheng_jt_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005002/005002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '交通工程'}), f2],

    ["gcjs_zhongbiaohx_jt_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005002/005002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '交通工程'}), f2],

    ["gcjs_zhongbiao_jt_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005002/005002004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '交通工程'}), f2],
    ####
    ["gcjs_zhaobiao_sl_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005003/005003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '水利工程'}), f2],

    ["gcjs_gqita_bian_cheng_sl_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005003/005003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '水利工程'}), f2],

    ["gcjs_zhongbiaohx_sl_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005003/005003003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '水利工程'}), f2],

    ["gcjs_zhongbiao_sl_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005003/005003004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gclx': '水利工程'}), f2],

    ####
    ["zfcg_zhaobiao_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005004/005004001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_cheng_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005004/005004002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005004/005004004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005004/005004003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ####
    ["jqita_zhaobiao_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005007/005007001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_gqita_bian_cheng_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005007/005007002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005007/005007003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "http://xnztb.xianning.gov.cn/xnweb/jyxx/005007/005007004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="湖北省咸宁市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_hubei_xianning"])


    # for d in data[2:]:
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


