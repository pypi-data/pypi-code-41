import pandas as pd  
import re
from selenium import webdriver 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from zlsrc.util.etl import est_meta,est_html




def f1(driver,num):
    locator=(By.XPATH,"//ul[@class='ewb-info-items']/li//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(re.findall("([0-9]{1,}).html",driver.current_url)[0])
    if num!=cnum:
        url=re.sub("([0-9]{1,})(?=\.html)",str(num),driver.current_url)
        val=driver.find_element_by_xpath("//ul[@class='ewb-info-items']/li//a").get_attribute('href')[-30:]
        driver.get(url)

        locator=(By.XPATH,"//ul[@class='ewb-info-items']/li//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    ul=soup.find("ul",class_="ewb-info-items")
    #ul=div.find("ul")
    lis=ul.find_all("li")
    data=[]
    for li in lis:
        a=li.find("a")
        ggstart_time=li.find("span").text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.xxggzy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    fonts=a.find_all("font")
    info={"quyu":fonts[0].text.strip()}
    if len(fonts)>=3:
        info["gctype"]=fonts[2].text.strip()
    df["info"]=json.dumps(info,ensure_ascii=False)
    return df 


def f2(driver):
    locator=(By.XPATH,"//span[contains(@class,'ewb-page-number')]")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    txt=driver.find_element_by_xpath("//span[contains(@class,'ewb-page-number')]").text.strip().split('/')[1]
    total=int(txt)
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH, "//div[@id='content']/div[contains(@style, 'margin-left')][string-length()>130]")
    WebDriverWait(driver,20).until(EC.presence_of_all_elements_located(locator))
    locator=(By.XPATH, "//td[@id='TDContent'][string-length()>130]")
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
    div=soup.find('div',id='content')
    return div

data=[

        ["gcjs_zhaobiao_gg","http://www.xxggzy.cn/jyxx/089003/089003001/1.html",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.xxggzy.cn/jyxx/089003/089003002/1.html",["name","ggstart_time","href","info"],f1,f2],


        ["gcjs_zhongbiaohx_gg","http://www.xxggzy.cn/jyxx/089003/089003003/1.html",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_gqita_gg","http://www.xxggzy.cn/jyxx/089003/089003004/1.html",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://www.xxggzy.cn/jyxx/089004/089004001/1.html",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.xxggzy.cn/jyxx/089004/089004002/1.html",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhongbiaohx_gg","http://www.xxggzy.cn/jyxx/089004/089004003/1.html",["name","ggstart_time","href","info"],f1,f2],

    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省新乡市",**args)
    est_html(conp,f=f3,**args)


# 修改日期：2019/7/8
if __name__=="__main__":
    work(conp=["postgres","since2015","192.168.3.171","henan","xinxiang"])


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
    # df = f3(driver, 'http://www.jyggjy.cn/TPFront/ZtbDetail/ZtbJsDetail.aspx?type=3&infoid=4e8ee343-d891-468c-b519-e0668de9e75c&categoryNum=005002004')
    # print(df)