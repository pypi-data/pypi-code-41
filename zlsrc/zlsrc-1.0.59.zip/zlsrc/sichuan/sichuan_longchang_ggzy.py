import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import add_info,est_meta,est_html,est_tbs



def f1_data(driver, num):
    locator = (By.XPATH, '(//*[@id="btnCheck"])[1]')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('onclick')
    try:
        locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Pager"]/table/tbody/tr/td[1]/font[3]/b')
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
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
        if 'ViewType=JJCGJJ&QuYu=LC' in url:
            try:
                title = tr.find_all('td', align="center")[2].text.strip()
            except:
                title = '-'
            try:
                td = tr.find_all('td', align="center")[3].text.strip()
            except:
                td = '-'
        else:
            try:
                title = tr.find_all('td', align="center")[3].text.strip()
            except:
                title = '-'
            try:
                td = tr.find_all('td', align="center")[5].text.strip()
            except:
                td = '-'
        try:
            onclick = tr.find_all('input', id="btnCheck")
            for each in onclick:
                onclick = each.get('onclick')
            link = re.findall(r"OpenUrl\('(.*)'\);", onclick)[0].strip()
            link = 'http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/GongGao_Detail.aspx?GongGaoGuid='+ link +'%20%20%20%20&ViewType=' + ViewType
        except:
            link = '-'
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1(driver, num):
    WebDriverWait(driver, 10).until(lambda driver: len(driver.current_url) > 10)
    url = driver.current_url
    if "http://wsjj.njztb.cn/njcg/" in url:
        df = f1_data(driver, num)
        return df
    locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//tr[@class="myGVPagerCss"]/td/span[1]')
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
        j = 0
    except:
        cnum = 1
        j = 1
    if num != int(cnum):
        while True:
            cnum = int(driver.find_element_by_xpath('//tr[@class="myGVPagerCss"]/td/span[1]').text.strip())

            val = driver.find_element_by_xpath(
                '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]').get_attribute('href')[-25:]

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
            locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"][not(contains(@href,"{}"))]'.format(val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_myGV')
    trs = table.find_all("tr")
    data = []
    i = -1
    if j ==1:
        i = None
    for tr in trs[1:i]:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        try:
            href = a['href'].strip()
            if "http" in href:
                link = href
            else:
                link = "http://ggzy.lcggzy.com/ceinwz/" + href
        except:
            link = '-'
        try:
            td = tr.find("td", class_="fFbDate")
            span = td.find('span').text.strip()
        except:
            span = '-'
        try:
            title = re.sub(r'^\[(.*)\]', '', title)
            if '※' in title:
                title = re.sub(r'※', '', title).strip()
        except:
            title = title
            if '※' in title:
                title = re.sub(r'※', '', title).strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    WebDriverWait(driver, 10).until(lambda driver: len(driver.current_url) > 10)
    global page_total
    url = driver.current_url
    if "http://wsjj.njztb.cn/njcg/" in url:
        locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Datagrid1"]/tbody/tr[2]/td[4]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_Pager"]/table/tbody/tr/td[1]/font[2]/b')
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            page_total = int(st)
        except:
            page_total = 1
        driver.quit()
        return int(page_total)
    else:
        locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl23_LabelPageCount"]')
            st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            page_total = int(st)
        except:
            page_total = 1
        driver.quit()
        return int(page_total)


def f3(driver, url):
    driver.get(url)
    url = driver.current_url
    if 'http://wsjj.njztb.cn/njcg/' in url:
        locator = (By.XPATH, "//table[@class='Table'][string-length()>30]")
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
        div = soup.find('span', id="ctl00_ContentPlaceHolder1_lblGongGaoContent")
        return div
    elif '/ceinwz/admin_show.aspx' in url:
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
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        page1 = driver.page_source
        soup1 = BeautifulSoup(page1, 'html.parser')
        div1 = soup1.find_all('table')[0]
        if 'id="frmBestwordHtml' in str(driver.page_source):
            driver.switch_to_frame('frmBestwordHtml')
            if '找不到文件或目录' in str(driver.page_source):
                return '找不到文件或目录'
            locator = (By.XPATH, "//div[contains(@class, 'Section')][string-length()>3] | //embed[@id='plugin']")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
            flag = 1
        else:
            locator = (By.XPATH, "//table[@width='75%'] | //div[@class='wrap'] | //div[@class='page']")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
     "http://ggzy.lcggzy.com/ceinwz/WebInfo_List.aspx?newsid=200&jsgc=0100000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzy.lcggzy.com/ceinwz/WebInfo_List.aspx?newsid=200&jsgc=0010000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://ggzy.lcggzy.com/ceinwz/WebInfo_List.aspx?newsid=200&jsgc=0000010&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzy.lcggzy.com/ceinwz/WebInfo_List.aspx?newsid=201&jsgc=&zfcg=0100000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=2&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://ggzy.lcggzy.com/ceinwz/WebInfo_List.aspx?newsid=203&jsgc=&zfcg=0000001&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://ggzy.lcggzy.com/ceinwz/WebInfo_List.aspx?newsid=202&jsgc=&zfcg=0010000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/JJGongGao_List.aspx?ViewType=JJGG&QuYu=LC",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'cgfs':'网上竞价'}), f2],

    ["zfcg_biangeng_wsjj_gg",
     "http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/JJGongGao_List.aspx?ViewType=JJGGBG&QuYu=LC",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'cgfs':'网上竞价'}), f2],

    ["zfcg_gqita_zhong_liu_wsjj_gg",
     "http://wsjj.njztb.cn/njcg/ZFCGZtbMis_NeiJiang/Pages/GongGaoChaKan/JJCJGongGao_List.aspx?ViewType=JJCGJJ&QuYu=LC",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'cgfs':'网上竞价'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省隆昌市",**args)
    est_html(conp,f=f3,**args)


# 修改时间：2019/7/31
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","longchang"],pageloadtimeout=60)

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
    #     df=f1(driver, 25)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # d = f3(driver, 'http://ggzy.lcggzy.com/ceinwz/hyzq/hyzbjggszfcg.aspx?sgzbbm=LCJY(2017)0049')
    # print(d)


