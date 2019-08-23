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





def f1(driver, num):
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
                '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]').get_attribute('href')[-15:]

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
    url = driver.current_url
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
                link = "http://jyggzy.my.gov.cn/ceinwz/" + href
        except:
            link = '-'
        try:
            td = tr.find("td", class_="fFbDate")
            span = td.find('span').text.strip()
        except:
            span = '-'
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
    global page_total
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
    if '/ceinwz/admin_show.aspx' in url:
        locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BodyLabel'][string-length()>60] | //table[@class='border_1' and @align='center'][string-length()>60]")
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
        div = soup.find('table', attrs={'class':'border_1', 'align':'center'})
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
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=100&jsgc=0100000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=101&jsgc=0010000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=102&jsgc=0000010&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgc",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=201&jsgc=&zfcg=0100000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_bu_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=202&jsgc=&zfcg=0010000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=203&jsgc=&zfcg=0000001&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_gg",
     "http://jyggzy.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=200&jsgc=&zfcg=0000100&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=zfcg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省江油市",**args)
    est_html(conp,f=f3,**args)


# 修改时间：2019/7/31
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","jiangyou"],pageloadtimeout=60)


    # for d in data[5:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 50)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://182.140.133.175/view/staticpags/shiji_gzgg/4028868744620b9801446330af490435.jsp')
    # print(df)


