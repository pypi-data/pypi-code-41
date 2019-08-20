import math
import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time



def f1(driver, num):
    locator = (By.XPATH, "//span[@id='currentid']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    locator = (By.XPATH, '//table[@width="948" and @cellpadding="0"]/../table[@width="100%"]/tbody/tr[1]//a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]

    if int(cnum) != int(num):
        js = '''
        function changepage(value){
        var jumpnum = value;
        var downpagelase = maxpage;
        var downpagelasecenter = maxpage ;
        var r = /^\+?[1-9][0-9]*$/;
        if(!r.test(jumpnum)){
        alert("跳转页数必须为正整数");
            return;
        }else if(jumpnum==""||jumpnum<=0||(jumpnum*1-1)>=(downpagelase*1)){
            alert("输入的页数必须大于0小于最大页数");
            return;
        }else if(jumpnum == 1){
            window.location.href=firsturl;
        }else{
            downpagelase = downpagelase*1-jumpnum+1;
            downpagelase = "000000000"+ downpagelase ;
            downpagelase = downpagelase .substring(downpagelase.length-9);                 
            baseurl= baseurl+"/"+schannelId.substring(0,7)+"/"+schannelId.substring(7,19)+"/"+downpagelase.substring(0,3)+"/"+downpagelase.substring(3,6)+"/c"+schannelId+"_"+downpagelase+".shtml";
            window.location.href=baseurl;
              }
        };
        changepage(%s);
                ''' % num
        driver.execute_script(js)

        locator = (By.XPATH, '//table[@width="948" and @cellpadding="0"]/../table[@width="100%%"]/tbody/tr[1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    page = driver.page_source
    body = etree.HTML(page)

    content_list = body.xpath('//table[@width="948" and @cellpadding="0"]/../table[@width="100%"]/tbody/tr')

    data = []
    for content in content_list:
        name = content.xpath(".//a/text()")[0].strip()
        ggstart_time = content.xpath("./td/table/tbody/tr/td[last()]/text()")[0].strip()
        url = content.xpath(".//a/@href")[0].strip()

        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@id='allid']")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    if '404 Not Found' in driver.page_source:
        return '404 Not Found'
    locator = (By.XPATH, "//table[@width='950' and @cellpadding='3']")
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
    soup = BeautifulSoup(page, 'lxml')
    div = soup.find('table', attrs={'width':'950','cellpadding':'3'})
    return div


data = [
    ["gcjs_zhaobiao_sg_gg",
     "http://bid.cnnb.com.cn/sg/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "施工"}), f2],
    ["gcjs_zhaobiao_kcsj_gg",
     "http://bid.cnnb.com.cn/kcsj/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "勘察设计"}), f2],
    ["gcjs_zhaobiao_jl_gg",
     "http://bid.cnnb.com.cn/jl/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "监理"}), f2],
    ["gcjs_gqita_zhong_zhao_gg",
     "http://bid.cnnb.com.cn/other/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "其他"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省宁波市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "gcjs_zhejiang_ningbo"]
    work(conp)
    # driver= webdriver.Chrome()
    # driver.get('http://bid.cnnb.com.cn/sg/')
    # f1(driver,4)
    # for d in data[-1:]:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     for i in range(1, total, 10):
    #         driver.get(d[1])
    #         print(d[1])
    #         df_list = f1(driver, i).values.tolist()
    #         print(df_list[:10])
    #         df1 = random.choice(df_list)
    #         print(str(f3(driver, df1[2]))[:100])
    #
