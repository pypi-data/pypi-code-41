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
from zlsrc.util.etl import est_meta,est_html,add_info


def f1(driver,num):
    locator=(By.XPATH,"//tbody[@id='index-list']//tr//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(driver.find_element_by_class_name("curr").text)
    if num!=cnum:
        val=driver.find_element_by_xpath("//tbody[@id='index-list']//tr[2]//a").get_attribute('href').rsplit('/', maxsplit=1)[1]
        driver.execute_script("kkpager._clickHandler(%s)"%str(num))
        time.sleep(1)
        locator=(By.XPATH,"//span[@class='ui-dialog-loading'][2]")
        WebDriverWait(driver,10).until(EC.invisibility_of_element_located(locator))

        locator=(By.XPATH,"//tbody[@id='index-list']//tr[2]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    div=soup.find("tbody",id="index-list")
    trs=div.find_all("tr")[1:]
    data=[]
    for tr in trs:
        a=tr.find("a")
        try:
            name=a['title'].strip()
        except:
            name = a.text.strip()
        td = tr.find("td", class_='text-center')
        ggstart_time = td.find('span').text.strip()
        href = "http://www.sqggzy.com"+a["href"]
        tmp=[name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator=(By.CLASS_NAME,"totalPageNum")
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    txt=driver.find_element_by_xpath("//span[@class='totalPageNum']").text.strip()
    total=int(txt)
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@class='art-content clearfix'][string-length()>40]")
    WebDriverWait(driver,20).until(EC.presence_of_all_elements_located(locator))

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
    div=soup.find('div',class_='art-content clearfix')
    return div


def switchto(f,gctype,ggtype):
    def wrap(*args):
        driver=args[0]
        locator=(By.XPATH,"//ul[@id='trade-info-menu-list']")
        WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
        driver.find_element_by_xpath("//ul[@id='trade-info-menu-list']/li[contains(string(),'%s')]"%gctype).click()
        time.sleep(1)

        locator=(By.XPATH,"//span[@class='ui-dialog-loading'][2]")

        WebDriverWait(driver,10).until(EC.invisibility_of_element_located(locator))

        locator=(By.XPATH,"//ul[@id='trade-list-item']")
        WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
        driver.find_element_by_xpath("//ul[@id='trade-list-item']/li[@style='display: list-item;'][contains(string(),'%s')]"%ggtype).click()
        time.sleep(1)

        locator=(By.XPATH,"//span[@class='ui-dialog-loading'][2]")

        WebDriverWait(driver,10).until(EC.invisibility_of_element_located(locator))
        df=f(*args)
        return df
    return wrap





data=[
        ["gcjs_zhaobiao_fangwu_gg","http://www.sqggzy.com/spweb/HNSQ/TradeCenter/tradeList.do?Deal_Type=Deal_Type1"
        ,["name","ggstart_time","href","info"],add_info(switchto(f1,"房建","招标"),{"gctype":"房建市政"}),f2],

        ["gcjs_zhaobiao_jiaotong_gg","http://www.sqggzy.com/spweb/HNSQ/TradeCenter/tradeList.do?Deal_Type=Deal_Type1"
        ,["name","ggstart_time","href","info"],add_info(switchto(f1,"交通","招标"),{"gctype":"交通"}),f2],

        ["gcjs_zhaobiao_shuili_gg","http://www.sqggzy.com/spweb/HNSQ/TradeCenter/tradeList.do?Deal_Type=Deal_Type1"
        ,["name","ggstart_time","href","info"],add_info(switchto(f1,"水利","招标"),{"gctype":"水利"}),f2],

        ["zfcg_zhaobiao_gg","http://www.sqggzy.com/spweb/HNSQ/TradeCenter/tradeList.do?Deal_Type=Deal_Type1"
        ,["name","ggstart_time","href","info"],switchto(f1,"政府采购","招标"),f2],


        ["zfcg_zhongbiao_gg","http://www.sqggzy.com/spweb/HNSQ/TradeCenter/tradeList.do?Deal_Type=Deal_Type4"
        ,["name","ggstart_time","href","info"],switchto(f1,"政府采购","结果公告"),f2],

        ["zfcg_gqita_gg","http://www.sqggzy.com/spweb/HNSQ/TradeCenter/tradeList.do?Deal_Type=Deal_Type1"
        ,["name","ggstart_time","href","info"],switchto(f1,"政府采购","其他公告"),f2],
    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省商丘市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","shangqiu"],num=1,total=2,html_total=10)


    # for d in data:
    #     url = d[1]
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     d1 = f2(driver)
    #     print(d1)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     d2 = f1(driver, 3)
    #     print(d2)
    #     for i in d2[2].values:
    #         df = f3(driver, i)
    #         print(df)
