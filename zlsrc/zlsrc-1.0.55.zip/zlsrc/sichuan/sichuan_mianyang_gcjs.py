import random

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

import time

from zlsrc.util.etl import est_html, est_meta, add_info




def f1_1(driver, num):
    locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_myGV']/tbody/tr[2]/td/a")
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    try:
        locator = (By.XPATH, "//tr[@class='myGVPagerCss']/td/span[1]")
        str = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(str)
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        while True:
            cnum = int(driver.find_element_by_xpath('//tr[@class="myGVPagerCss"]/td/span[1]').text.strip())

            val = driver.find_element_by_xpath(
                "//table[@id='ctl00_ContentPlaceHolder1_myGV']/tbody/tr[2]/td/a").get_attribute('href')[-15:]

            if cnum > num:
                if cnum - num > page_total // 2:
                    first_b = driver.find_element_by_xpath(
                        '//a[contains(@id, "LinkButtonFirstPage")]')
                    driver.execute_script("arguments[0].click()", first_b)
                else:
                    pre_b = driver.find_element_by_xpath(
                        '//a[contains(@id, "LinkButtonPreviousPage")]')
                    driver.execute_script("arguments[0].click()", pre_b)

            elif cnum < num:
                if num - cnum > page_total // 2:
                    last_b = driver.find_element_by_xpath(
                        '//a[contains(@id, "LinkButtonLastPage")]')
                    driver.execute_script("arguments[0].click()", last_b)
                else:
                    nex_b = driver.find_element_by_xpath(
                        '//a[contains(@id, "LinkButtonNextPage")]')
                    driver.execute_script("arguments[0].click()", nex_b)

            else:
                break
            # 第二个等待
            locator = (By.XPATH,
                       '//table[@id="ctl00_ContentPlaceHolder1_myGV"]/tbody/tr[2]/td/a[not(contains(@href,"{}"))]'.format(
                           val))
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_myGV')
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:-1]:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        if 'http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?' in url:
            link = "http://ztb.my.gov.cn/ceinwz/" + a['href'].strip()
        else:
            link = "http://caigou.my.gov.cn/ceinwz/" + a['href'].strip()
        try:
            td = tr.find("td", class_="fFbDate")
            span = td.find_all('span')[0].text.strip()
        except:
            span = '-'
        try:
            title = re.sub(r'\[(.*?)\]', '', title).strip()
            if '※' in title:
                title = re.sub(r'※', '', title).strip()
        except:
            title = title
            if '※' in title:
                title = re.sub(r'※', '', title).strip()
        tmp = [title, span, link]
        data.append(tmp)
        # print(tmp)
        # t = f3(driver, link)
        # print(t)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1_2(driver, num):
    locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a")
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
    try:
        locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_lblPage']")
        str = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'第(\d+)页', str)[0]
        d = -1
    except:
        cnum = 1
        d = 0

    url = driver.current_url

    if num != int(cnum):
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_inPageNum']")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_inPageNum']")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).send_keys(num)
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_Button1']")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).click()

        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV')
    trs = table.find_all("tr")
    data = []
    for tr in trs[:d]:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        if "http://ztb.my.gov.cn/ceinwz/xwmore.aspx?" in url:
            link = "http://ztb.my.gov.cn/ceinwz/" + a['href'].strip()
        else:
            link = "http://caigou.my.gov.cn/ceinwz/" + a['href'].strip()
        try:
            span = re.findall(r'\((\d+-\d+-\d+)\)', title)[0]
        except:
            span = '-'
        tmp = [title, span, link]
        data.append(tmp)
        # print(tmp)
        # t = f3(driver, link)
        # print(t)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1_3(driver, num):
    locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span")
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    try:
        locator = (By.XPATH, "//tr[@class='myGVPagerCss']/td[@colspan='3']/table/tbody/tr/td/span")
        s = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(s)
    except:
        cnum = 1

    url = driver.current_url

    if num != int(cnum):
        driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$Tabs$tabpnlEnsure$myGVEnsure','Page${}')".format(num))
        try:
            locator = (By.XPATH,"//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span[not(contains(string(), '%s'))]" % val)
            WebDriverWait(driver, 1).until(EC.presence_of_element_located(locator))
        except:
            driver.back()
            while True:
                driver.find_element_by_xpath("(//tr[@class='myGVPagerCss']//a)[last()-1]").click()
                locator = (By.XPATH, "(//tr[@class='myGVPagerCss']//a)[last()-1]")
                WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
                time.sleep(3)
                page = driver.page_source
                soup = BeautifulSoup(page, 'html.parser')
                trs = soup.find_all('tr', class_='myGVPagerCss')
                ss = 0
                for tr in trs:
                    ts = tr.find_all('a')
                    for t in ts:
                        t_num = t.text.strip()
                        if str(num) == str(t_num):
                            ss = 1
                            break
                if ss == 1:
                    break
            driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$Tabs$tabpnlEnsure$myGVEnsure','Page${}')".format(num))
            locator = (By.XPATH,"//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span[not(contains(string(), '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure')
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:-2]:
        a = tr.find("span")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "-"
        try:
            span = tr.find_all('td')[1].text.strip()
        except:
            span = '-'
        try:
            td = tr.find_all('td')[2].text.strip()
            tds = re.findall(r'\((.*)\)', td)
            td = tds[0] if tds else td
        except:
            td = None
        yy = {"yuanyin": td}
        info = json.dumps(yy, ensure_ascii=False)

        tmp = [title, span, link, info]
        data.append(tmp)
        # print(tmp)
        # t = f3(driver, link)
        # print(t)
    df = pd.DataFrame(data)
    return df


def f1(driver, num):
    url = driver.current_url
    if 'WebInfo_List.aspx?' in url:
        df = f1_1(driver, num)
        return df
    elif 'xwmore.aspx?' in url:
        df = f1_2(driver, num)
        return df
    elif 'cxzbxm.aspx?' in url:
        df = f1_3(driver, num)
        return df


def f2(driver):
    WebDriverWait(driver, 10).until(lambda driver:len(driver.current_url)>10)
    global page_total
    url = driver.current_url
    if 'WebInfo_List.aspx?' in url:
        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_myGV']/tbody/tr[2]/td/a")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_myGV_ctl23_LabelPageCount']")
            page_total = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip())
        except:
            page_total = 1
    elif 'xwmore.aspx?' in url:
        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_lblPage']")
            str = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
            page_total = int(re.findall(r'共(\d+)页', str)[0])
        except:
            page_total = 1
    elif 'http://ztb.my.gov.cn/ceinwz/cxzbxm.aspx?' in url:
        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span")
        val_1 = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        try:
            driver.find_element_by_link_text('>>').click()
            locator = (By.XPATH,
                       "//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span[not(contains(string(), '%s'))]" % val_1)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

            locator = (By.XPATH, "//tr[@class='myGVPagerCss']/td/table/tbody/tr/td[last()]/span")
            page_total = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip())
        except:
            page_total = 1
    driver.quit()
    return int(page_total)



def f3(driver, url):
    driver.get(url)
    if '/ceinwz/admin_show.aspx' in url:
        locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BodyLabel'][string-length()>60] | //table[@width='100%' and @style='margin-top:6px;'][string-length()>60]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        before = len(driver.page_source)
        time.sleep(1)
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
        div = soup.find('table', attrs={'width': '100%','style':'margin-top:6px;'})
        return div
    else:
        time.sleep(2)
        locator = (By.XPATH, "//table[@width='100%'][string-length()>100]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        page1 = driver.page_source
        soup1 = BeautifulSoup(page1, 'html.parser')
        div1 = soup1.find_all('table')[0]
        if 'id="frmBestwordHtml' in str(driver.page_source):
            driver.switch_to_frame('frmBestwordHtml')
            if '找不到文件或目录' in str(driver.page_source):
                return '找不到文件或目录'
            locator = (By.XPATH, "//div[contains(@class, 'Section')][string-length()>3] | //embed[@id='plugin'] | //body[contains(@style, 'height')]")
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
            flag = 1
        else:
            locator = (By.XPATH, "//table[@width='75%'] | //div[@class='wrap'] | //div[@class='page']")
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
            flag = 2

        before = len(driver.page_source)
        time.sleep(1)
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
        if flag == 1:
            div = soup.find('body')
            if div == None:
                div = soup.find('embed', id='plugin')
            divs1 = str(div1) + str(div)
            div = BeautifulSoup(divs1, 'html.parser')
        elif flag == 2:
            div = soup.find_all('table')[0]
        else:
            raise ValueError
        return div

data = [
    ["gcjs_zhaobiao_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=100,106,112,118,124,130,136,142,148,154&jsgc=0100000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["gcjs_zhongbiao_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=103,109,115,121,127,133,139,145,151,157&jsgc=0000010&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_biangeng_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=104,110,116,122,128,134,140,146,152,158&jsgc=0000000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["gcjs_liubiao_gg",
     "http://ztb.my.gov.cn/ceinwz/cxzbxm.aspx?xmlx=10&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_cailiao_shiji_gg",
     "http://ztb.my.gov.cn/ceinwz/xwmore.aspx?id=200,206,212,218,224,230,236,242,248,254&qxid=1&FromUrl=sbcllzb11",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'设备材料类项目招标(市本级)'}), f2],

    ["gcjs_zhongbiao_cailiao_shiji_gg",
     "http://ztb.my.gov.cn/ceinwz/xwmore.aspx?id=203,209,215,221,227,233,239,245,251,257&qxid=1&FromUrl=sbcllzb",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'设备材料类项目招标(市本级)'}), f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?jsgc=0011000&newsid=101,107,113,119,125,131,137,,143,149,155&qxid=1&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_cailiao_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=200,206,212,218,224,230,236,242,248,254&jsgc=0000000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=1&ShowOverDate=0&showdate=1&FromUrl=sbcllzb11",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'设备材料类'}), f2],

    ["gcjs_gqita_bian_bu_cailiao_gg",
     "http://ztb.my.gov.cn/ceinwz/xwmore.aspx?id=201,207,213,219,225,131,237,243,249,255&qxid=1&FromUrl=sbcllzb",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'设备材料类'}), f2],

    ["gcjs_zhongbiaohx_cailiao_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=203,209,215,221,227,233,239,245,251,257&jsgc=0000000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=1&ShowOverDate=0&showdate=1&FromUrl=sbcllzb",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '设备材料类'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省绵阳市", **args)
    est_html(conp, f=f3, **args)

# 修改时间：2019/8/15
if __name__ == '__main__':
    work(conp=["postgres", "zlsrc.com.cn", "192.168.4.200", "sichuan", "sichuan_mianyang_gcjs"],pageloadtimeout=120,pageloadstrategy="none")

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
    #     df=f1(driver, 285)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)