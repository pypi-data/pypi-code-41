
import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json


# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="https://ggzy.changsha.gov.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

from zlsrc.util.etl import add_info,est_meta,est_html,est_tbs




def f1_data(driver, num):
    locator = (By.XPATH, '(//*[@id="btnCheck"])[1]')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('onclick')
    try:
        locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Pager"]/table/tbody/tr/td[1]/font[3]/b')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(str)
    except:
        cnum = 1
    if num != int(cnum):
        driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$Pager','{}')".format(num))
        try:
            locator = (By.XPATH, "(//*[@id='btnCheck'])[1][not(contains(@onclick, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Pager"]/table/tbody/tr/td[1]/font[3]/b')
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnn = int(st)
            if cnn != num:
                raise TimeoutError

    url = driver.current_url
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_Datagrid1')
    trs = table.find_all("tr")
    data = []
    ViewType = re.findall(r'ViewType=(.*)&', url)[0]
    for tr in trs[1:]:
        info = {}
        t={}
        if ('ViewType=JJGG&QuYu=SBJ' in url) or ('ViewType=JJGGBG&QuYu=SBJ' in url):
            try:
                title = tr.find_all('td', align="center")[3].text.strip()
            except:
                title = '-'
            try:
                td = tr.find_all('td', align="center")[5].text.strip()
            except:
                td = '-'
            if tr.find_all('td', align="center")[6]:
                endtime = tr.find_all('td', align="center")[6].text.strip()
                if endtime:info['endtime'] = endtime
            if tr.find('td', align="right"):
                ysje = tr.find('td', align="right").text.strip()
                if ysje:info['ysje'] = ysje
            t['title']= title
            t['ggstart_time'] = td
        elif 'ViewType=JJCGJJ&QuYu=SBJ' in url:
            try:
                title = tr.find_all('td', align="center")[2].text.strip()
            except:
                title = '-'
            try:
                td = tr.find_all('td', align="center")[3].text.strip()
            except:
                td = '-'
            if tr.find_all('td', align="center")[6]:
                htje = tr.find_all('td', align="center")[6].text.strip()
                if htje:info['htje'] = htje
            if tr.find_all('td', align="center")[7]:
                ysje = tr.find_all('td', align="center")[7].text.strip()
                if ysje:info['ysje'] = ysje
            t['title']= title
            t['ggstart_time'] = td
        elif 'ViewType=ZGCJGG&QuYu=SBJ' in url:
            try:
                title = tr.find_all('td', align="center")[2].text.strip()
            except:
                title = '-'
            try:
                td = tr.find_all('td', align="center")[5].text.strip()
            except:
                td = '-'
            if tr.find('td', align="right"):
                ysje = tr.find('td', align="right").text.strip()
                if ysje:info['ysje'] = ysje
            t['title']= title
            t['ggstart_time'] = td
        elif 'ViewType=ZGGG&QuYu=SBJ' in url:
            try:
                title = tr.find_all('td', align="center")[2].text.strip()
            except:
                title = '-'
            try:
                td = tr.find_all('td', align="center")[4].text.strip()
            except:
                td = '-'
            if tr.find('td', align="right"):
                ysje = tr.find('td', align="right").text.strip()
                if ysje:info['ysje'] = ysje
            t['title']= title
            t['ggstart_time'] = td
        try:
            onclick = tr.find_all('input', id="btnCheck")
            for each in onclick:
                onclick = each.get('onclick')
            link = re.findall(r"OpenUrl\('(.*)'\);", onclick)[0].strip()
            link = 'http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/GongGao_Detail.aspx?GongGaoGuid='+ link +'%20%20%20%20&ViewType=' + ViewType
        except:
            link = '-'
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        title = t['title']
        ggstart_time = t['ggstart_time']
        tmp = [title, ggstart_time, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2_data(driver, num):
    url = driver.current_url
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table")
    trs = table.find_all("tr")
    data = []
    for tr in trs:
        try:
            title = tr.find_all('td')[1]
            title = title['title'].strip()
        except:
            title = '-'
        try:
            td = tr.find_all('td')[2].text.strip()
            td = re.findall(r'(\d+-\d+-\d+)', td)[0]
        except:
            td = '-'

        link = '-'
        try:
            span = tr.find_all('td')[3].text.strip()
            a={"yunyin":span}
            a=json.dumps(a,ensure_ascii=False)
            info=a
        except:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f3_data(driver, num):
    locator = (By.XPATH, "//div[@class='pageright']/ul/li[1]/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-13:]
    try:
        locator = (By.XPATH, "//td[@align='right']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)/', str)[0]
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        if "channels/113_" not in url:
            s = "113_%d" % (num) if num > 1 else "113"
            url = re.sub("113", s, url)
        elif num == 1:
            url = re.sub("113_[0-9]*", "113", url)
        else:
            s = "113_%d" % (num) if num > 1 else "113"
            url = re.sub("113_[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='pageright']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="pageright")
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "http://ggzy.neijiang.gov.cn" + a['href'].strip()
        td = tr.find("span", class_="more").text.strip()
        span = re.findall(r'\[(.*)\]', td)[0]
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1(driver, num):
    url = driver.current_url
    if "http://wsjj.njztb.cn/njcg/" in url:
        df = f1_data(driver, num)
        return df
    elif ('http://ztb.njztb.cn/ceinwz/cxzbxmEnsure_first.aspx' in url) or ('http://zfcg.njztb.cn/ceinwz/cxzbxm_first.aspx' in url) or ("http://zfcg.njztb.cn/ceinwz/cxzbxmEnsure_first.aspx" in url):
        df = f2_data(driver, num)
        return df
    elif 'http://ggzy.neijiang.gov.cn/channels' in url:
        df = f3_data(driver, num)
        return df
    else:
        locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        try:
            locator = (By.XPATH, '//tr[@class="myGVPagerCss"]/td/span[1]')
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = int(st)
        except:
            cnum = 1
        url = driver.current_url
        if num != int(cnum):
            while True:
                cnum = int(driver.find_element_by_xpath('//tr[@class="myGVPagerCss"]/td/span[1]').text.strip())

                val = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]').get_attribute('href')[-30:]

                if cnum > num:
                    if cnum - num > page_total // 2:
                        first_b = driver.find_element_by_xpath('//a[contains(@id, "LinkButtonFirstPage")]')
                        driver.execute_script("arguments[0].click()", first_b)
                    else:
                        pre_b = driver.find_element_by_xpath('//a[contains(@id, "LinkButtonPreviousPage")]')
                        driver.execute_script("arguments[0].click()", pre_b)

                elif cnum < num:
                    if num - cnum > page_total // 2:
                        last_b = driver.find_element_by_xpath('//a[contains(@id, "LinkButtonLastPage")]')
                        driver.execute_script("arguments[0].click()", last_b)
                    else:
                        nex_b = driver.find_element_by_xpath('//a[contains(@id, "LinkButtonNextPage")]')
                        driver.execute_script("arguments[0].click()", nex_b)
                else:
                    break
                # 第二个等待
                locator = (By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"][not(contains(@href,"{}"))]'.format(val))
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find("table", id='ctl00_ContentPlaceHolder1_myGV')
        trs = table.find_all("tr")
        data = []
        for tr in trs[1:-1]:
            a = tr.find('a')
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            if "http://ztb.njztb.cn/ceinwz/" in url:
                link = "http://ztb.njztb.cn/ceinwz/" + a['href'].strip()
            if "http://zfcg.njztb.cn/ceinwz/" in url:
                link = "http://zfcg.njztb.cn/ceinwz/" + a['href'].strip()
            td = tr.find("td", class_="fFbDate")
            span = td.find('span').text.strip()
            try:
                title = re.sub(r'\[(.*)\]', '', title).strip()
                if '※' in title:
                    title = re.sub(r'※', '', title).strip()
            except:
                if '※' in title:
                    title = re.sub(r'※', '', title).strip()
                title = title
            tmp = [title, span, link]
            data.append(tmp)
        df = pd.DataFrame(data)
        df['info'] = None
        return df





def f2(driver):
    WebDriverWait(driver, 10).until(lambda driver: len(driver.current_url) > 10)
    global page_total
    url = driver.current_url
    if ('http://ztb.njztb.cn/ceinwz/cxzbxmEnsure_first.aspx' in url) or ('http://zfcg.njztb.cn/ceinwz/cxzbxm_first.aspx' in url) or ("http://zfcg.njztb.cn/ceinwz/cxzbxmEnsure_first.aspx" in url):
        page_total = 1
    elif "http://wsjj.njztb.cn/" in url:
        locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Datagrid1"]/tbody/tr[2]/td[4]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Pager"]/table/tbody/tr/td[1]/font[2]/b')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            page_total = int(str)
        except:
            page_total = 1
        driver.quit()
        return int(page_total)
    elif 'http://ggzy.neijiang.gov.cn/channels' in url:
        locator = (By.XPATH, "//div[@class='pageright']/ul/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, '//td[@align="right"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            page_total = int(re.findall(r'/(\d+)', str)[0])
        except:
            page_total = 1
        driver.quit()
        return int(page_total)
    else:
        locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl23_LabelPageCount"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            page_total = int(str)
        except:
            page_total = 1
    driver.quit()
    return int(page_total)



def f3(driver, url):
    driver.get(url)
    url = driver.current_url
    if re.findall(r'\.pdf$', url):
        return url
    if 'http://wsjj.njztb.cn/njcg/' in url:
        locator = (By.XPATH, "//td[@class='TableSpecial'][string-length()>60]")
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
        div = soup.find('span', id="ctl00_ContentPlaceHolder1_lblGongGaoContent")
        return div
    elif '/ceinwz/admin_show.aspx' in url:
        locator = (By.XPATH, "//div[@class='newsImage'][string-length()>60]")
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
        div = soup.find('div', class_="newsImage")
        n = 5
        while div.name !='table' and n >0:
            div = div.parent
            n-=1
        if div == None:raise ValueError
        return div
    else:
        locator = (By.XPATH, "//table[@width='100%'][string-length()>100]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        page1 = driver.page_source
        soup1 = BeautifulSoup(page1, 'html.parser')
        div1 = soup1.find_all('table')[0]
        if 'id="frmBestwordHtml' in str(driver.page_source):
            driver.switch_to_frame('frmBestwordHtml')
            if '找不到文件或目录' in str(driver.page_source):
                return '找不到文件或目录'
            locator = (By.XPATH, "//div[contains(@class, 'Section')][string-length()>3] | //embed[@id='plugin'] | //body[contains(@style, 'height')]")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
            flag = 1
        else:
            locator = (By.XPATH, "//table[@width='75%'] | //div[@class='wrap'] | //div[@class='page']")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
            flag = 2

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
        if flag == 1:
            div = soup.find('body')
            if div == None:
                div = soup.find('embed', id='plugin')
            divs1 = str(div1)+str(div)
            div = BeautifulSoup(divs1, 'html.parser')
        elif flag == 2:
            div = soup.find_all('table')[0]
        else:raise ValueError
        return div

data = [
    ["gcjs_zhaobiao_gg",
     "http://ztb.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=0&jsgc=0100000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ztb.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=0&jsgc=0010000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_dayi_gg",
     "http://ztb.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=0&jsgc=0001000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://ztb.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=0&jsgc=0000010&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://ztb.njztb.cn/ceinwz/cxzbxmEnsure_first.aspx?num=10000&len=14&gif=bullet&cellspacing=1&cellpadding=1&zwnr=1&more=1&fontsize=14px",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_hetong_gg",
     "http://ztb.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=0&jsgc=0000000001&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_qita_gg",
     "http://ztb.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=0&jsgc=&zfcg=&tdjy=&cqjy=&qtjy=0100000000&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他交易'}),f2],

    ["gcjs_zhongbiao_qita_gg",
     "http://ztb.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=0&jsgc=&zfcg=&tdjy=&cqjy=&qtjy=0000010000&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'其他交易'}),f2],

    ["zfcg_zhaobiao_gg",
     "http://zfcg.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=201&jsgc=&zfcg=0100000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=2&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_bian_bu_gg",
     "http://zfcg.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=202&jsgc=&zfcg=0010000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "http://zfcg.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=203&jsgc=&zfcg=0000010&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://zfcg.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=203&jsgc=&zfcg=0000001&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_lx1_gg",
     "http://zfcg.njztb.cn/ceinwz/cxzbxm_first.aspx?num=10000&len=16&fontsize=14px&cellspacing=1&cellpadding=1&FromUrl=cxzb&more=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_lx2_gg",
     "http://zfcg.njztb.cn/ceinwz/cxzbxmEnsure_first.aspx?num=10000&len=16&fontsize=14px&cellspacing=1&cellpadding=1&FromUrl=cxzb&more=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_ercixunjia_gg",
     "http://zfcg.njztb.cn/ceinwz/WebInfo_List.aspx?newsid=0&jsgc=&zfcg=0100000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=1&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上二次询价'}), f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/JJGongGao_List.aspx?ViewType=JJGG&QuYu=SBJ",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_biangeng_wsjj_gg",
     "http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/JJGongGao_List.aspx?ViewType=JJGGBG&QuYu=SBJ",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_gqita_zhong_liu_wsjj_gg",
     "http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/JJCJGongGao_List.aspx?ViewType=JJCGJJ&QuYu=SBJ",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_zhaobiao_zhigou_gg",
     "http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/GongGao_List.aspx?ViewType=ZGGG&QuYu=SBJ",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'直购'}), f2],

    ["zfcg_gqita_zhong_liu_zhigou_gg",
     "http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/GongGao_List.aspx?ViewType=ZGCJGG&QuYu=SBJ",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'直购'}), f2],

    ["qsy_gqita_zhao_zhong_gg",
     "http://ggzy.neijiang.gov.cn/channels/113.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'社会交易'}), f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省内江市",**args)
    est_html(conp,f=f3,**args)


# 修改时间：2019/8/15
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","neijiang"],image_show_gg=2,pageloadtimeout=160,pageloadstrategy="none", num=1, headless=False)

    #
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoList/GongGao_Detail.aspx?GongGaoGuid=0c887e8d-3134-43a2-9df0-ce2dec670525&ViewType=JJCGJJ')
    # print(df)
    #
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
    #     df=f1(driver, 120)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
