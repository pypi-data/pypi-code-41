import pandas as pd  
import re
from selenium import webdriver 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, est_meta, add_info



def f1(driver,num):
    locator = (By.XPATH, "//div[@class='column-info-list']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=int(re.findall('ing=(\d+)',url)[0])

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='column-info-list']/ul/li[1]/a").get_attribute('href')[-35:]
        url=re.sub('(?<=ing=)\d+',str(num),url)
        driver.get(url)

        locator = (By.XPATH, "//div[@class='column-info-list']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator=(By.XPATH,"//div[@class='column-info-list']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    div=soup.find("div",class_="column-info-list")
    ul=div.find("ul")
    lis=ul.find_all("li",class_="clearfix")
    data=[]
    for li in lis:
        a=li.find("a")
        try:
            title = a["title"]
        except:
            title = a.text.strip()
        span=li.find("span")
        link = "http://ggzy.zhaoqing.gov.cn"+a["href"]
        tmp = [title, span.text.strip(), link]
        print(tmp)
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    locator=(By.XPATH,"//div[@class='column-info-list']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    try:
        total=driver.find_element_by_xpath("//a[@class='wb-page-default wb-page-number wb-page-family'] | //td[@class='huifont']").text.split("/")[1]
        total=int(total)
    except:
        total = 1
    driver.quit()
    return total

def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH, "//div[@class='menu-info'][string-length()>30]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    before=len(driver.page_source)
    time.sleep(0.1)
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
    div=soup.find('div',class_="menu-info")
    return div


data=[
    # ["gcjs_zhaobiao_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003001/003001001/?pageing=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    # ["gcjs_zhongbiaohx_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003001/003001002/?pageing=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    # ["gcjs_zhongbiao_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003001/003001003/?pageing=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://ggzy.zhaoqing.gov.cn/sh/showinfo/moreinfolist.aspx?categorynum=003002001&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_biangeng_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003002/003002002/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003002/003002003/?pageing=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["qsy_zhaobiao_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003006/003006001/?pageing=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'一般招标'}), f2],
    #
    ["qsy_gqita_bian_bu_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003006/003006002/?pageing=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'一般招标'}), f2],
    #
    ["qsy_zhongbiaohx_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003006/003006003/?pageing=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'一般招标'}), f2],
    #
    ["qsy_zhongbiao_gg", "http://ggzy.zhaoqing.gov.cn/sh/jyxx/003006/003006004/?pageing=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'一般招标'}), f2],

    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省四会市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","guangdong","sihui"],num=1,headless=False,ipNum=0,cdc_total=100)

    # driver=webdriver.Chrome()
    # url = "http://ggzy.zhaoqing.gov.cn/sh/showinfo/moreinfolist.aspx?categorynum=003002001"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://ggzy.zhaoqing.gov.cn/sh/showinfo/moreinfolist.aspx?categorynum=003002001"
    # driver.get(url)
    # for i in range(1, 5):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for m in df[2].values:
    #         f = f3(driver, m)
    #         print(f)