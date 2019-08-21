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

from zlsrc.util.etl import est_meta, est_html, add_info



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='vF_detail_main']|//div[@class='vF_deail_maincontent']|//div[@class='vT_z w760']")
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
    div = soup.find('div', class_="vF_detail_main")
    if not div:
        div = soup.find('div', class_="vF_deail_maincontent")
        if not div:
            div = soup.find('body')
    return div


def f1(driver, num):
    if 'eadylynotice' in driver.current_url:
        locator = (By.XPATH, "//div[@class='inforcon']/ul/li[not(contains(@style,'display: none;'))][1]/a")
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
        locator = (By.XPATH, '//strong[@id="spanPageNum"]')
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

        if int(cnum) != int(num):
            js = """function next(page1){  
              hideTable(); 
              currentRow = pageSize * (page1 -1);  
              maxRow = currentRow + pageSize;  
              if ( maxRow > numberRowsInTable ) maxRow = numberRowsInTable;  
              for ( var i = currentRow; i< maxRow; i++ ){  
            theUL.getElementsByTagName("li")[i].style.display = '';  
              }  
               page = page1; 
              if ( maxRow == numberRowsInTable ) {
               nextText();
               lastText();
              }  
              showPage();  
              preLink();  
              firstLink();
              displayTotal();
            
             
             // dolist(); 
            }  ;next(%s)
            """%num
            driver.execute_script(js)
            locator = (By.XPATH, '//div[@class="inforcon"]/ul/li[not(contains(@style,"display: none;"))][1]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath("//div[@class='inforcon']/ul/li[not(contains(@style,'display: none;'))]")
        for content in content_list:
            name = content.xpath("./a/@title")[0].strip()
            ggstart_time = content.xpath("./span/text()")[0].strip()


            url = 'http://www.ccgp.gov.cn/eadylynotice' + content.xpath("./a/@href")[0].strip('.').strip()
            info = json.dumps({}, ensure_ascii=False)
            temp = [name, ggstart_time, url, info]
            data.append(temp)

    else:

        locator = (By.XPATH, '//ul[@class="c_list_bid"]/li[1]/a|//ul[@class="ulst"]/li[1]/a')
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
        locator = (By.XPATH, '//span[@class="current"]')
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

        if int(cnum) != int(num):
            url = re.sub('index[_\d]*', 'index_' + str(num - 1), driver.current_url)
            driver.get(url)
            locator = (By.XPATH, '//ul[@class="c_list_bid"]/li[1]/a|//ul[@class="ulst"]/li[1]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))

        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//ul[@class="c_list_bid"]/li|//ul[@class="ulst"]/li')
        for content in content_list:
            name = content.xpath("./a/@title")[0].strip()
            ggstart_time = content.xpath("./em[2]/text()|./span[2]/text()")[0].strip()
            ggtype = content.xpath("./em[1]/text()|./span[1]/text()")
            area = content.xpath("./em[3]/text()|./span[1]/text()")
            buyer = content.xpath("./em[4]/text()|./span[1]/text()")
            if "zygg" in driver.current_url:
                url_pre = '/'.join(driver.current_url.split('/')[:-1])
                url = url_pre + content.xpath("./a/@href")[0].strip().strip('.')
            else:
                if "dfgg" in driver.current_url:
                    url = 'http://www.ccgp.gov.cn/cggg/dfgg' + content.xpath("./a/@href")[0].strip().strip('.')
                else:
                    url = 'http://www.ccgp.gov.cn/' + content.xpath("./a/@href")[0].strip().strip('../../..')
            info = json.dumps({"ggtype": ggtype, 'area': area, 'buyer': buyer}, ensure_ascii=False)
            temp = [name, ggstart_time, url, info]

            data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    if 'eadylynotice' in driver.current_url:
        locator = (By.XPATH, '//strong[@id="spanTotalPage"]')
        total_page = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text

    else:
        locator = (By.XPATH, '//p[@class="pager"]/a[last()-1]')
        total_page = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text

    driver.quit()
    return int(total_page)


data = [
    #
    ["gcjs_dyly_gg",
     "http://www.ccgp.gov.cn/eadylynotice/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    #
    ["gcjs_zhaobiao_1_gg",
     "http://www.ccgp.gov.cn/cggg/zygg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '中央'}), f2],
    # #
    ["gcjs_zhaobiao_gg",
     "http://www.ccgp.gov.cn/cggg/dfgg/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'tag': '地方'}), f2],
    #
    ["gcjs_zhaobiao_zygjjgplcg_gg",
     "http://www.ccgp.gov.cn/zydwplcg/zy/zyzb/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "中央国家机关批量集中采购公告"}), f2],

    #
    ["gcjs_zhongbiao_zygjjgplcg_gg",
     "http://www.ccgp.gov.cn/zydwplcg/zy/zyzhb/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "中央国家机关批量集中采购公告"}), f2],

    #
    ["gcjs_zhaobiao_zyzsjgplcg_gg",
     "http://www.ccgp.gov.cn/zydwplcg/zz/zzzb/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "中央直属机关批量集中采购公告"}), f2],

    #
    ["gcjs_zhongbiao_zyzsjgplcg_gg",
     "http://www.ccgp.gov.cn/zydwplcg/zz/zzzhb/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"tag": "中央直属机关批量集中采购公告"}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="全国政府采购", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    # pass
    # for d in data[1:]:
    #
    #     driver = webdriver.Chrome()
    #     url = d[1]
    #     driver.get(url)
    #     df = f1(driver, 2)
    #     print(d[1])
    #     for u in df.values.tolist()[:4]:
    #         print(str(f3(driver, u[2]))[:100])
    #     driver.get(url)
    #     print(f2(driver))
    # driver= webdriver.Chrome()
    # print(f3(driver, 'http://www.ccgp.gov.cn/cggg/zygg/gkzb/201507/t20150701_5493905.htm'))
    #     print(f2(driver))
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest", "bc_qg_zfcg"])
