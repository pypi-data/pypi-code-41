import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import  est_meta, est_html, add_info



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="xxx-main"]/ul/li[not(@class)][1]/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute("href")[-30:]
    cnum = int(driver.find_element_by_xpath("//span[@class='cPageNum']").text)
    if cnum != num:
        driver.execute_script("pageNav.go(%d)" % num)
        time.sleep(0.2)
        locator=(By.XPATH,"//div[@class='xxx-main']/ul/li[not(@class)][1]/a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("ul", id="list")
    lis = ul.find_all("li", recursive=False)[1:]
    data = []
    for li in lis:
        a = li.find("a")
        span = li.find("span")
        name = a["title"]
        name = re.sub("【.*】", "", name)
        href = "http://ggzy.shaoyang.gov.cn" + a["href"]
        ggstart_time = span.text.strip()
        tmp = [name,  ggstart_time,href]
        data.append(tmp)

    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.ID, "pageNav")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        total = int(re.findall('共([0-9]*)页', driver.find_element_by_id("pageNav").get_attribute("title"))[0])
    except StaleElementReferenceException:
        total = int(re.findall('共([0-9]*)页', driver.find_element_by_id("pageNav").get_attribute("title"))[0])
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//iframe[@class='ugly']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page1 = driver.page_source

    soup1 = BeautifulSoup(page1, 'html.parser')
    div = str(soup1.find('div',id='timeBanner'))

    for i in driver.find_elements_by_xpath("//iframe[@class='ugly']"):
        driver.switch_to.frame(i)
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

        div2 = soup.find('div',class_='content')
        div += str(div2)
        driver.switch_to_default_content()

    return div


def switch_to(driver, xmtype, ggtype):
    locator = (By.XPATH, '//div[@class="xxx-main"]/ul/li[not(@class)][1]/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute("href")[-30:]
    cxmtype = driver.find_element_by_xpath("//div[@class='newsType on']").text

    if xmtype != cxmtype:
        driver.find_element_by_xpath("//div[@class='newsType'][contains(string(), '%s')]" % xmtype).click()
        time.sleep(0.2)
        locator=(By.XPATH,"//div[@class='xxx-main']/ul/li[not(@class)][1]/a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    cggtype = driver.find_element_by_xpath("//div[@class='site-bar']//button[@class='btn-site on']").text

    if ggtype != cggtype:
        driver.find_element_by_xpath("//div[@class='site-bar']//button[contains(string(), '%s')]" % ggtype).click()
        time.sleep(0.2)
        locator=(By.XPATH,"//div[@class='xxx-main']/ul/li[not(@class)][1]/a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


def gcjs(f, ggtype):
    def wrap(*krg):
        driver = krg[0]
        switch_to(driver, "工程建设", ggtype)
        if f == f1:
            df = f(*krg)
            if '\u2003' in ggtype:
                types = ggtype.replace('\u2003', '')
            else:
                types = ggtype
            a = {"yuan_ggtype": types}
            a = json.dumps(a, ensure_ascii=False)
            df["info"] = a
            return df
        else:
            return f(*krg)

    return wrap


def zfcg(f, ggtype):
    def wrap(*krg):
        driver = krg[0]
        switch_to(driver, "政府采购", ggtype)
        if f == f1:
            df = f(*krg)
            if '\u2003' in ggtype:
                types = ggtype.replace('\u2003', '')
            else:
                types = ggtype
            a = {"yuan_ggtype": types}
            a = json.dumps(a, ensure_ascii=False)
            df["info"] = a
            return df
        else:
            return f(*krg)

    return wrap


data = [

    ["gcjs_zhaobiao_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "ggstart_time", "href", "info"], gcjs(f1, "招标公告"), gcjs(f2, "招标公告")],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "ggstart_time", "href", "info"], gcjs(f1, "补充通知"), gcjs(f2, "补充通知")],

    ["gcjs_gqita_bian_da_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "ggstart_time", "href", "info"], gcjs(f1, "答 疑"), gcjs(f2, "答 疑")],

    ["gcjs_zhongbiaohx_sjg_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "ggstart_time", "href", "info"], gcjs(f1, "入围公示"), gcjs(f2, "入围公示")],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&xtype=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
        , ["name", "ggstart_time", "href", "info"], gcjs(f1, "中标候选人公示"), gcjs(f2, "中标候选人公示")],
    # 政府采购

    ["zfcg_zhaobiao_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "ggstart_time", "href", "info"], zfcg(f1, "采购公告"), zfcg(f2, "采购公告")],

    ["zfcg_gqita_bian_bu_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "ggstart_time", "href", "info"], zfcg(f1, "补充通知"), zfcg(f2, "补充通知")],

    ##连接失效
    # ["zfcg_gqita_bian_da_gg",
    #  "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
    #     , ["name", "ggstart_time", "href", "info"], zfcg(f1, "答 疑"), zfcg(f2, "答 疑")],

    ["zfcg_zhongbiao_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "ggstart_time", "href", "info"], zfcg(f1, "中标公示"), zfcg(f2, "中标公示")],

    ["zfcg_hetong_gg",
     "http://ggzy.shaoyang.gov.cn/newsList.html?index=5&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&ext=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD"
        , ["name", "ggstart_time", "href", "info"], zfcg(f1, "合同公示"), zfcg(f2, "合同公示")],

]


def work(conp, **args):
    est_meta(conp, data, diqu="湖南省邵阳市", **args)
    est_html(conp, f3, **args)


# work(conp=["postgres","since2015","127.0.0.1","hunan","shaoyang"])
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "hunan", "shaoyang"],num=1)
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     # if d[0].startswith('zfcg'):
    #
    #     df = eval(d[4]).values.tolist()
    #     print(df)
    #     for k in df[:1]:
    #         print(k[2])
    #         print(f3(driver, k[2]))
    #     driver.get(d[1])
    #     print(eval(d[5]))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://ggzy.shaoyang.gov.cn/新流程/招投标信息/jyxx_1.aspx?iq=cg&type=招标公告&tpid=5b87ae5cf0480678a4339579'))