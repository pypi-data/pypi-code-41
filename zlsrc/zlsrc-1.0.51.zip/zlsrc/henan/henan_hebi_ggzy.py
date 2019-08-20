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
from zlsrc.util.etl import est_meta,est_html



def f1(driver,num):
    locator=(By.XPATH,"//td[@class='border3']//tr//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("Paging=([0-9]{1,})",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("(?<=Paging=)([0-9]{1,})",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//td[@class='border3']//tr[1]//a").get_attribute('href')[-40:]
        driver.get(url)

        locator=(By.XPATH,"//td[@class='border3']//tr[1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    div=soup.find("td",class_="border3")
    #ul=div.find("ul")
    trs=div.find_all("tr",height="30")
    data=[]
    for tr in trs:
        a=tr.find("a")
        ggstart_time=tr.find_all("td")[-1].text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://ggzy.hebi.gov.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    locator=(By.CLASS_NAME,"pagemargin")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath("//td[@class='huifont']").text.split("/")[1]
    total=int(total)
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    time.sleep(0.5)
    try:
        locator = (By.XPATH,"//div[contains(@id,'menutab') and @style='']//td[@id='TDContent'][string-length()>300] | //div[contains(@id,'menutab') and not(@style)]//td[@id='TDContent'][string-length()>300]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    except:
        locator=(By.XPATH,"//td[@width='998'][string-length()>30]")
        WebDriverWait(driver,2).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find("div", id=re.compile("menutab.*"), style="")
    if div ==  None:
        div = soup.find('td', width='998')
    return div

data=[
        ["gcjs_zhaobiao_gg","http://ggzy.hebi.gov.cn/TPFront/gcjs/013001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://ggzy.hebi.gov.cn/TPFront/gcjs/013002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://ggzy.hebi.gov.cn/TPFront/gcjs/013003/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://ggzy.hebi.gov.cn/TPFront/gcjs/013004/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_yucai_gg","http://ggzy.hebi.gov.cn/TPFront/zfcg/014001/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://ggzy.hebi.gov.cn/TPFront/zfcg/014002/?Paging=1",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_biangeng_gg","http://ggzy.hebi.gov.cn/TPFront/zfcg/014003/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiaohx_gg","http://ggzy.hebi.gov.cn/TPFront/zfcg/014004/?Paging=1",["name","ggstart_time","href","info"],f1,f2],

    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省鹤壁市",**args)
    est_html(conp,f=f3,**args)


# 修改日期：2019/7/10
if __name__=="__main__":
    work(conp=["postgres","since2015","192.168.3.171","henan","hebi"])
    #
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
    #     df=f1(driver, 3)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://ggzy.hebi.gov.cn/TPFront/showinfo/ZtbJyxxDetail.aspx?type=3&InfoID=35b2434f-2738-41d5-b3b8-1e76a4a2113d&CategoryNum=014004')
    # print(df)