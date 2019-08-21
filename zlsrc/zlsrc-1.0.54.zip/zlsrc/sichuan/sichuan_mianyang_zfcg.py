import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_html, est_meta, add_info



def f1_1(driver, num):
    locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_myGV']/tbody/tr[2]/td/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    try:
        locator = (By.XPATH, "//tr[@class='myGVPagerCss']/td/span[1]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(str)
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        while True:
            cnum = int(driver.find_element_by_xpath('//tr[@class="myGVPagerCss"]/td/span[1]').text.strip())

            val = driver.find_element_by_xpath(
                "//table[@id='ctl00_ContentPlaceHolder1_myGV']/tbody/tr[2]/td/a").get_attribute('href')[-25:]

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
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1_2(driver, num):
    locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    try:
        locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_lblPage']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'第(\d+)页', str)[0]
        d = -1
    except:
        cnum = 1
        d = 0

    url = driver.current_url

    if num != int(cnum):
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_inPageNum']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_inPageNum']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num)
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_Button1']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()

        locator = (By.XPATH,
                   "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1(driver, num):
    url = driver.current_url
    if 'WebInfo_List.aspx?' in url:
        df = f1_1(driver, num)
        return df
    elif 'xwmore.aspx?' in url:
        df = f1_2(driver, num)
        return df


def f2(driver):
    WebDriverWait(driver, 10).until(lambda driver: len(driver.current_url) > 10)
    global page_total
    url = driver.current_url
    if 'WebInfo_List.aspx?' in url:
        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_myGV']/tbody/tr[2]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_myGV_ctl23_LabelPageCount']")
            page_total = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip())
        except:
            page_total = 1
    elif 'xwmore.aspx?' in url:
        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_lblPage']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            page_total = int(re.findall(r'共(\d+)页', str)[0])
        except:
            page_total = 1
    driver.quit()
    return int(page_total)


def f3(driver, url):
    driver.get(url)
    if '/ceinwz/admin_show.aspx' in url:
        locator = (By.XPATH, "//div[@class='newsImage'][string-length()>30]")
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
        div = soup.find('div', class_="newsImage")
        n = 5
        while div.name !='table' and n >0:
            div = div.parent
            n-=1
        if div == None:raise ValueError
        return div
    else:
        locator = (By.XPATH, "//table[@width='75%'][string-length()>30]")
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
        page1 = driver.page_source
        soup1 = BeautifulSoup(page1, 'html.parser')
        div1 = soup1.find('table', width='75%')
        if '<iframe id="frmBestwordHtml' in driver.page_source:
            driver.switch_to_frame('frmBestwordHtml')
            flag = 1
            locator = (By.XPATH,
                       "//div[@class='WordSection1'][string-length()>3] | //div[@class='Section1'][string-length()>3] | //body[string-length()>10]")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        else:
            flag = 2
            locator = (By.XPATH,
                       "//table[@width='75%'][string-length()>30] | //div[@class='wrap'][string-length()>30] | //div[@id='content'][string-length()>30]")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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
        if flag == 1:
            div = soup.find('div', class_='WordSection1')
            if div == None:
                div = soup.find('div', class_='Section1')
                if div == None:
                    div = soup.find('body')
        else:
            div = soup.find('table', width="75%")
            if div == None:
                div = soup.find('div', class_='wrap')
                if div == None:
                    div = soup.find('div', id='content')
        div2 = str(div1) + str(div)
        div3 = BeautifulSoup(div2, 'html.parser')
        return div3


data = [
    ["zfcg_dyly_gg",
     "http://caigou.my.gov.cn/ceinwz/xwmore.aspx?id=400&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_yucai_gg",
     "http://caigou.my.gov.cn/ceinwz/xwmore.aspx?id=401&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhaobiao_shiji_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=601&jsgc=&zfcg=0100000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_gqita_bian_bu_shiji_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=602&jsgc=&zfcg=0010000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_gqita_zhong_liu_shiji_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=604&jsgc=&zfcg=0000010&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_zhaobiao_quxian_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=2000&jsgc=&zfcg=0000000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区'}), f2],
    #
    ["zfcg_biangeng_quxian_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=3000&jsgc=&zfcg=0000000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区'}), f2],
    #
    ["zfcg_zhongbiao_quxian_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=5000&jsgc=&zfcg=0000000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省绵阳市", **args)
    est_html(conp, f=f3, **args)

# 修改时间：2019/8/15
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "mianyang"], pageloadtimeout=60,
         pageLoadStrategy="none")

    # driver=webdriver.Chrome()
    # url = "http://caigou.my.gov.cn/ceinwz/hyzq/hyzbjggszfcg.aspx?sgzbbm=MYZC%d5%d0(2017)93%ba%c5"
    # df = f3(driver, url)
    # print(df)


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
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         print(f)
    #         d = f3(driver, f)
    #         print(d)
