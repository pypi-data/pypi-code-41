import random
import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from zlsrc.util.etl import  est_html, est_tbs, est_meta_large




def f1_data(driver, num):
    # driver.maximize_window()
    locator = (By.XPATH, "//td[@class='table4']//table/tbody/tr[last()-1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//font[@class='pagenow']/b")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    if num != int(cnum):
        val = driver.find_element_by_xpath("//td[@class='table4']//table/tbody/tr[last()-1]//a").get_attribute('href')[-40:]

        driver.find_element_by_xpath("//input[contains(@name, 'GV')]").clear()
        driver.find_element_by_xpath("//input[contains(@name, 'GV')]").send_keys(num)

        locator = (By.XPATH, "//font[@class='gopage']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()

        locator = (By.XPATH, "//td[@class='table4']//table/tbody/tr[last()-1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id=re.compile("GV"))
    # print(table)
    lis = table.tbody.find_all("tr")
    data = []
    for li in lis[1:-1]:
        if not li.find("a"):
            continue
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = 'http://www.sdzfcg.gov.cn/site/Page/Information/' + a['href']
        span = li.find("td", align="center").text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f1(driver, num):
    url = driver.current_url
    if "Page/Information/AffichePage.aspx" in url:
        df = f1_data(driver, num)
        return df

    locator = (By.XPATH, "//ul[@class='article-list-a']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        locator = (By.XPATH, "//ul[@class='pages-list']/li[1]/a")
        page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)/', page)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='article-list-a']/li[last()]//a").get_attribute('href')[-35:]
        url = driver.current_url
        url = re.sub('queryContent_[0-9]+-','queryContent_%d-'% num, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='article-list-a']/li[last()]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("ul", class_="article-list-a")
    lis = ul.find_all("li")
    s = 0
    data = []
    for li in lis:
        s+=1
        info = {}
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = None
        handle = driver.current_window_handle
        driver.find_element_by_xpath("//ul[@class='article-list-a']/li[{}]/div/a".format(s)).click()
        handles = driver.window_handles
        for newhandle in handles:
            if newhandle != handle:
                # 切换到新打开的窗口B
                time.sleep(random.uniform(1, 3))
                driver.switch_to_window(newhandle)
                link = driver.current_url
                driver.close()
                driver.switch_to_window(handle)

        span = li.find("div", class_="list-times").text.strip()
        if re.findall(r'【(.*?)】', title):
            diqu = re.findall(r'【(.*?)】', title)[0]
            info['diqu'] = diqu
        t = int(len(li.find_all("div", class_='list-t')))
        if t==3:
            if li.find_all("div", class_='list-t')[-2]:
                ywlx = li.find_all("div", class_='list-t')[-2].text.strip()
                info['ywlx'] = ywlx
            if li.find_all("div", class_='list-t')[-1]:
                gglx  = li.find_all("div", class_='list-t')[-1].text.strip()
                info['gglx'] = gglx
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        if link==None:raise ValueError
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    url = driver.current_url
    if "Page/Information/AffichePage.aspx" in url:
        locator = (By.XPATH, "//td[@class='table4']//table/tbody/tr[last()-1]//a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        locator = (By.XPATH, "//font[@class='pagecount']/b")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        driver.quit()
        return int(num)

    else:
        # channelId = re.findall(r'channelId=(\d+)', url)[0]
        locator = (By.XPATH, "//ul[@class='article-list-a']/li[last()]//a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        locator = (By.XPATH, "//ul[@class='pages-list']/li[1]/a")
        page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)', page)[0]
        driver.quit()
        return int(num)


def f3(driver,url):
    driver.get(url)
    if 'http://www.sdzfcg.gov.cn/site/Page/Information/' in url:
        locator = (By.XPATH, "//td[@class='table4'][string-length()>130]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
        div = soup.find('td', class_='table4')
        return div

    locator=(By.XPATH,"//table[@class='gycq-table'][string-length()>10]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    before=len(driver.page_source)
    time.sleep(0.5)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find('div',class_='content')
    if div == None:raise ValueError('div not find')
    return div


def zfcg_zb(f):
    def warp(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//span[contains(@id, 'lb_Nevigator')]")
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if '采购公告' not in val_1:
            driver.execute_script("javascript:__doPostBack('btn_Link','')")

            locator = (By.XPATH, "//span[@id='lb_Nevigator']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp


def zfcg_bg(f):
    def warp(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//span[contains(@id, 'lb_Nevigator')]")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if "更正公告" not in val:
            driver.execute_script("javascript:__doPostBack('btn_Link2','')")

            locator = (By.XPATH, "//span[@id='lb_Nevigator2']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return warp


def zfcg_zhongb(f):
    def warp(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//span[contains(@id, 'lb_Nevigator')]")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if "中标公告" not in val:
            driver.execute_script("javascript:__doPostBack('btn_Link3','')")

            locator = (By.XPATH, "//span[@id='lb_Nevigator3']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)

    return warp




data = [
        ["gcjs_zhaobiao_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgg.jspx?channelId=78",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_zhongbiaohx_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgs.jspx?channelId=149",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_zhongbiao_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgs.jspx?channelId=87",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        #
        ["zfcg_zhaobiao_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgg.jspx?channelId=79",
         ["name", "ggstart_time", "href","info"],f1,f2],
        #
        ["zfcg_zhongbiao_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgs.jspx?channelId=79",
         ["name", "ggstart_time", "href","info"],f1,f2],


        ["yiliao_zhaobiao_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgg.jspx?channelId=84",
         ["name", "ggstart_time", "href","info"],f1,f2],
        #
        ["yiliao_zhongbiao_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgs.jspx?channelId=84",
         ["name", "ggstart_time", "href","info"],f1,f2],


        ["jqita_zhaobiao_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgg.jspx?channelId=162",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["jqita_zhongbiao_gg", "http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgs.jspx?channelId=162",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ####zfcg

        ["zfcg_zhaobiao_lx1_gg", "http://www.sdzfcg.gov.cn/site/Page/Information/AffichePage.aspx",
         ["name", "ggstart_time", "href", "info"], zfcg_zb(f1), zfcg_zb(f2)],

        ["zfcg_biangeng_lx1_gg", "http://www.sdzfcg.gov.cn/site/Page/Information/AffichePage.aspx",
         ["name", "ggstart_time", "href", "info"], zfcg_bg(f1), zfcg_bg(f2)],

        ["zfcg_zhongbiao_lx1_gg", "http://www.sdzfcg.gov.cn/site/Page/Information/AffichePage.aspx",
         ["name", "ggstart_time", "href", "info"], zfcg_zhongb(f1), zfcg_zhongb(f2)],

]



def work(conp,**args):
    est_meta_large(conp,data=data,diqu="山东省",**args)
    est_html(conp,f=f3,**args)


# 网址新增：http://ggzyjy.shandong.gov.cn/queryContent_1-jyxxgg.jspx?channelId=79  修改时间：2019/6/10
# 最新修改日期：2019/8/14
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","shandong2"],num=1)


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
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://ggzyjy.shandong.gov.cn/yxzgysgg/b0qFZOCKMqCTn2iOrSazHA.jhtml?type=1 ')
    # print(df)
