import math
import re

import pandas as pd
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, add_info, est_meta_large
from zlsrc.util.fake_useragent import UserAgent



def switch_to(f, ggtype):
    def warp(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//div[@class='panel-heading-search']/div/a[@class='active']")
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 != ggtype:
            locator = (By.XPATH, "//table[@id='bulletinlistid']/tbody/tr[last()]//a")
            va1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('data-bulletin_id')

            click_button = driver.find_element_by_xpath("//div[@class='panel-heading-search']/div/a[contains(string(), '%s')]//b" % ggtype)
            driver.execute_script("arguments[0].click()", click_button)
            locator = (By.XPATH, "//table[@id='bulletinlistid']/tbody/tr[last()]//a[not(contains(@data-bulletin_id, '%s'))]"% va1)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        locator = (By.XPATH, "//div[@class='panel-heading-search']/div/a[@class='active'][contains(string(), '%s')]"% ggtype)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        tnum = int(driver.find_element_by_xpath("//span[@class='dropdown-text']").text.strip())
        if tnum != 100:
            locator = (By.XPATH, "//table[@id='bulletinlistid']/tbody/tr[last()]//a")
            va2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('data-bulletin_id')

            driver.find_element_by_xpath("//div[@class='dropdown btn-group'][1]/button[@data-toggle='dropdown']").click()
            locator = (By.XPATH, "//div[@class='dropdown btn-group open'][1]/button[@data-toggle='dropdown' and @aria-expanded='true']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            driver.find_element_by_xpath("//a[@data-action='100']").click()
            # 第一个等待
            locator = (By.XPATH, "//span[@class='text-default'][contains(string(), '100')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            # 第二个等待
            locator = (By.XPATH, "//table[@id='bulletinlistid']/tbody/tr[last()]//a[not(contains(@data-bulletin_id, '%s'))]"% va2)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp




def f1(driver, num):
    locator = (By.XPATH, "//table[@id='bulletinlistid']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//li[@aria-selected='true']/a[@class='button']")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())

    if num != int(cnum):
        while True:
            cnum = int(driver.find_element_by_xpath("//li[@aria-selected='true']/a[@class='button']").text.strip())
            num_list = driver.find_elements_by_xpath("//ul[@class='pagination']/li/a")

            nlist = []
            for nl in num_list:
                nlist.append(nl.text.strip())
            val = driver.find_element_by_xpath("//table[@id='bulletinlistid']/tbody/tr[last()]//a").get_attribute('data-bulletin_id')
            if (str(num) in nlist) and (cnum != num):
                time.sleep(3)
                nex_c = driver.find_element_by_xpath("//li[contains(@class, 'page')][contains(string(), '{}')]/a".format(str(num)))
                driver.execute_script("arguments[0].click()", nex_c)

            elif cnum > num:
                if cnum - num > total_num // 2:
                    first_b = driver.find_element_by_xpath("//a[@data-page='first']")
                    driver.execute_script("arguments[0].click()", first_b)
                else:
                    pre_b = driver.find_element_by_xpath("//li[contains(@class, 'page')][1]/a")
                    driver.execute_script("arguments[0].click()", pre_b)

            elif cnum < num:
                if num - cnum > total_num // 2:
                    last_b = driver.find_element_by_xpath("//a[@data-page='last']")
                    driver.execute_script("arguments[0].click()", last_b)
                else:
                    nex_b = driver.find_element_by_xpath("//li[contains(@class, 'page')][last()]/a")
                    driver.execute_script("arguments[0].click()", nex_b)
            else:
                break
            # 第二个等待
            locator = (By.XPATH, '//table[@id="bulletinlistid"]/tbody/tr[last()]//a[not(contains(@data-bulletin_id,"{}"))]'.format(val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", id="bulletinlistid").tbody
    trs = tbody.find_all("tr")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            name = tr.find('td', class_='text-left')['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('td', class_='text-center')[-1].text.strip()

        info_id = a['data-bulletin_id']
        if flag=='dyly':
            href = 'http://www.yngp.com/newbulletin_zz.do?method=toaddmodify&operator_state=1&lxflag=dy&flag=view&bulletin_id=' + info_id
        elif flag=='jkcp':
            href = 'http://www.yngp.com/newbulletin_zz.do?method=toaddmodify&operator_state=1&lxflag=jk&flag=view&bulletin_id=' + info_id
        else:
            href = 'http://www.yngp.com/newbulletin_zz.do?method=preinsertgomodify&operator_state=1&flag=view&bulletin_id=' + info_id


        try:
            gglx = tr.find_all('td', class_='text-center')[-3].text.strip()
            diqu = tr.find_all('td', class_='text-center')[-2].text.strip()
            info = {'gglx': '{}'.format(gglx), 'diqu': '{}'.format(diqu)}
            info = json.dumps(info, ensure_ascii=False)
        except:
            info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    global total_num,flag
    url = driver.current_url
    flag = url.rsplit('&', maxsplit=1)[1]
    locator = (By.XPATH, "//table[@id='bulletinlistid']/tbody/tr[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath("//span[@class='text-default']").text.strip()
    total_num = int(re.findall(r'\d+', total)[-1])
    total_num = math.ceil(total_num/100)
    driver.quit()
    return total_num





def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='searchPanel'][string-length()>10] | //div[@class='panel-body'][string-length()>30]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', id='searchPanel')
    if div == None:
        div = soup.find('div', class_='panel-body').parent
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.yngp.com/bulletin.do?method=moreList&zb",
     ["name", "ggstart_time", "href", "info"], switch_to(f1, '招标/预审/谈判/磋商/询价公告'), switch_to(f2, '招标/预审/谈判/磋商/询价公告')],
    #
    ["zfcg_gqita_zhao_zhong_ppp_gg",
     "http://www.yngp.com/bulletin.do?method=moreList&ppp",
     ["name", "ggstart_time", "href", "info"], switch_to(add_info(f1, {'gglx': 'PPP合作伙伴采购信息'}), 'PPP合作伙伴采购信息'), switch_to(f2, 'PPP合作伙伴采购信息')],
    # #
    ["zfcg_dyly_gg",
     "http://www.yngp.com/bulletin.do?method=moreList&dyly",
     ["name", "ggstart_time", "href", "info"], switch_to(f1, '单一来源审核前公示'), switch_to(f2, '单一来源审核前公示')],
    # #
    ["zfcg_zhaobiao_jkcp_gg",
     "http://www.yngp.com/bulletin.do?method=moreList&jkcp",
     ["name", "ggstart_time", "href", "info"], switch_to(add_info(f1, {'zbfs': '进口产品'}), '进口产品核准前公示'), switch_to(f2, '进口产品核准前公示')],
    # #
    ["zfcg_zhongbiao_gg",
     "http://www.yngp.com/bulletin.do?method=moreList&zhongb",
     ["name", "ggstart_time", "href", "info"], switch_to(f1, '中标、成交公告'), switch_to(f2, '中标、成交公告')],
    # #
    ["zfcg_gqita_bian_zhongz_gg",
     "http://www.yngp.com/bulletin.do?method=moreList&bgzz",
     ["name", "ggstart_time", "href", "info"], switch_to(f1, '澄清、更正、终止公告'), switch_to(f2, '澄清、更正、终止公告')],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="云南省",interval_page=300, **args)
    est_html(conp, f=f3, **args)


# 修改日期:2019/8/1
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "yunnan"])
    #

    #
    # for d in data[5:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = d[-1](driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=d[-2](driver, 70)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)