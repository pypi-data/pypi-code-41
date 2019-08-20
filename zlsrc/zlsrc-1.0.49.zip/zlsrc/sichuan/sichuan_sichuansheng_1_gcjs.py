import json
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zlsrc.util.etl import est_meta, est_html, add_info,est_meta_large



def f3(driver, url):
    driver.get(url)
    if "请输入正确的用户名和密码！" in str(driver.page_source):
        return '本网页需要注册，才可以爬取'
    locator = (By.XPATH, '//div[@id="mid_box"]|//table[@class="kuang"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', id="mid_box")
    if not div :
        div = soup.find('table', class_="kuang")
    return div




def f1(driver, num):
    if "WinnerNotice" in driver.current_url:

        locator = (By.XPATH, '//table[@class="lie"]/tbody/tr[position()!=1][1]/td/a')
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-10:]

        locator = (By.XPATH, '//span[@style="margin-right:5px;font-weight:Bold;color:red;"]')
        cnum = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
        if int(cnum) != int(num):
            driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$myPager','%s')" % num)

            locator = (By.XPATH, '//table[@class="lie"]/tbody/tr[position()!=1][1]/td/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//table[@class="lie"]/tbody/tr[position()!=1]')
        for content in content_list:
            name = content.xpath("./td/a/@title")[0].strip()
            ggstart_time = 'None'
            url = 'http://www.sccin.com.cn/InvestmentInfo/ZhaoBiao/' + content.xpath("./td/a/@href")[0].strip()
            area = content.xpath("./td[2]/span/text()")[0].strip()
            info = json.dumps({'area': area}, ensure_ascii=False)
            temp = [name, ggstart_time, url, info]
            data.append(temp)
        df = pd.DataFrame(data=data)

    elif "houxuanren" in driver.current_url :

        locator = (By.XPATH, '//td[@width="100%"]/table/tbody/tr[1]/td/a')
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-10:]

        locator = (By.XPATH, '//span[@style="margin-right:5px;font-weight:Bold;color:red;"]')
        cnum = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
        if int(cnum) != int(num):
            driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$myPager','%s')" % num)

            locator = (By.XPATH, '//td[@width="100%%"]/table/tbody/tr[1]/td/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//td[@width="100%"]/table/tbody/tr')
        for content in content_list:
            name = content.xpath("./td/a/@title")[0].strip()
            ggstart_time = content.xpath("./td[3]/text()")[0].strip()
            url = 'http://www.sccin.com.cn/InvestmentInfo/ZhaoBiao/' + content.xpath("./td/a/@href")[0].strip()

            area = content.xpath("./td[2]/text()")[0].strip()
            info = json.dumps({'area': area}, ensure_ascii=False)
            temp = [name, ggstart_time, url, info]
            data.append(temp)
        df = pd.DataFrame(data=data)
    elif "InvitNotice" not in driver.current_url:


        locator = (By.XPATH, '//td[@colspan="4"]/table/tbody/tr[2]/td[@valign="top"]/table/tbody/tr/td[2]/a')
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]

        locator = (By.XPATH, '//span[@id="ContentPlaceHolder1_DpList_lblCurrentPage"]')
        cnum = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
        if int(cnum) != int(num):

            driver.find_element_by_id("ContentPlaceHolder1_DpList_txtSelectPage").clear()
            driver.find_element_by_id("ContentPlaceHolder1_DpList_txtSelectPage").send_keys(num)
            driver.find_element_by_id("ContentPlaceHolder1_DpList_btnSure").click()

            locator = (By.XPATH, '//td[@colspan="4"]/table/tbody/tr[2]/td[@valign="top"]/table/tbody/tr/td[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//table/tbody/tr[3]/td[@colspan="4"]/table/tbody/tr[position()!=1]')
        for content in content_list:
            name = content.xpath("./td/table/tbody/tr/td[2]/a/@title")[0].strip()
            ggstart_time = content.xpath("./td/table/tbody/tr/td[4]/span/text()")[0].strip()
            url = 'http://www.sccin.com.cn/InvestmentInfo/TenderInfo/' + content.xpath("./td/table/tbody/tr/td[2]/a/@href")[0].strip()
            company = content.xpath("./td/table/tbody/tr/td[3]/text()")[0].strip()
            area = content.xpath("./td/table/tbody/tr/td[last()]/text()")[0].strip()
            info = json.dumps({'company':company,'area':area},ensure_ascii=False)
            temp = [name, ggstart_time, url,info]
            data.append(temp)
        df = pd.DataFrame(data=data)

    else:
        flag = int(driver.current_url[-1])
        if flag:
            driver.execute_script("showsub_a(1)")
        else: driver.execute_script("showsub_a(0)")


        locator = (By.XPATH, '//div[contains(@id,"sub")][@style="" or not(@style)]//table[contains(@id,"ContentPlaceHolder1")]/tbody/tr[child::td][1]/td/a')
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-10:]

        locator = (By.XPATH, '//div[contains(@id,"sub")][@style="" or not(@style)]//span[@style="margin-right:5px;font-weight:Bold;color:red;"]')
        cnum = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
        if int(cnum) != int(num):
            if not flag :
                driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$myPager','%s')"%num)#招标公告信息
            else:
                driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$myPager0','%s')"%num)#预审公告信息

            locator = (By.XPATH, '//div[contains(@id,"sub")][@style="" or not(@style)]//table[contains(@id,"ContentPlaceHolder1")]/tbody/tr[child::td][1]/td/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//div[contains(@id,"sub")][@style="" or not(@style)]//table[contains(@id,"ContentPlaceHolder1")]/tbody/tr[child::td]')
        for content in content_list:
            name = content.xpath("./td/a/span/@title")[0].strip()
            ggstart_time = content.xpath("./td[3]/text()")[0].strip()
            ggend_time = content.xpath("./td[4]/text()")[0].strip()
            if content.xpath("./td[2]/span/text()"):
                area = content.xpath("./td[2]/span/text()")[0].strip()
            else:area =""
            url = 'http://www.sccin.com.cn/InvestmentInfo/ZhaoBiao/' + content.xpath("./td/a/@href")[0].strip()
            info = json.dumps({'ggend_time':ggend_time,'area':area},ensure_ascii=False)
            temp = [name, ggstart_time, url,info]
            data.append(temp)
        df = pd.DataFrame(data=data)
    return df


def f2(driver):
    WebDriverWait(driver, 10).until(lambda driver: len(driver.current_url) > 10)
    if "houxuanren" in driver.current_url or "WinnerNotice" in driver.current_url:
        locator = (By.XPATH, '//div[@id="ContentPlaceHolder1_myPager"]')
        txt = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
        total_page = re.findall("共(\d+)页", txt)[0]
    elif "InvitNotice" not in driver.current_url:
        locator = (By.XPATH, '//span[@id="ContentPlaceHolder1_DpList_lblTotalPage"]')
        total_page = WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text

    else:
        flag = int(driver.current_url[-1])
        if flag:driver.execute_script("showsub_a(1)")
        else: driver.execute_script("showsub_a(0)")
        locator = (By.XPATH, '//div[contains(@id,"sub")][@style="" or not(@style)]//div[contains(@id,"Pager")]/div[1]')
        txt =  WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator)).text
        total_page = re.findall("共(\d+)页",txt)[0]
    driver.quit()
    return int(total_page)




data = [
    #
    ["gcjs_zhaobiao_gg",
     "http://www.sccin.com.cn/InvestmentInfo/TenderInfo/ZhaobiaoXinxi.aspx?area=local",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zgys_gg",
     "http://www.sccin.com.cn/InvestmentInfo/ZhaoBiao/InvitNotice.aspx?typeid=0&&type=ZBGG0",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhaobiao_1_gg",
     "http://www.sccin.com.cn/InvestmentInfo/ZhaoBiao/InvitNotice.aspx?typeid=0&&type=ZBGG1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_zhongbiaohx_gg",
     "http://www.sccin.com.cn/InvestmentInfo/ZhaoBiao/houxuanren.aspx?type=ZBHXR",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiao_gg",
     "http://www.sccin.com.cn/InvestmentInfo/ZhaoBiao/WinnerNotice.aspx?type=ZBJG",
     ["name", "ggstart_time", "href", "info"], f1, f2],



]


def work(conp, **arg):
    est_meta_large(conp, data=data, diqu="四川省", **arg)
    est_html(conp, f=f3, **arg)

# 修改时间：2019/8/15
if __name__ == '__main__':
    #
    # for d in data[3:]:
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
    #         print(f)
    #         d = f3(driver, f)
    #         print(d)

    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "sichuansheng"])
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.sccin.com.cn/InvestmentInfo/ZhaoBiao/DetaileWinner.aspx?id=203657'))
    # print(f2(driver))