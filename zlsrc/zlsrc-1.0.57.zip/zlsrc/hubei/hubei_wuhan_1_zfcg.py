import json
import time
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zlsrc.util.etl import est_meta, est_html



def f1(driver, num):
    locator = (By.XPATH, '//body/pre[string-length()>50]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//body/pre[contains(string(),"count")]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url = driver.current_url

    cnum = int(re.findall("pageNo=(\d+)&", url)[0])

    if num != cnum:
        val=driver.find_element_by_xpath('//body/pre').text[75:100]

        url = re.sub('(?<=pageNo=)\d+',str(num),url)

        page_count=len(driver.page_source)

        driver.get(url)

        locator = (By.XPATH, '//body/pre[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver:len(driver.page_source) != page_count)

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    contents=soup.find('pre').get_text()
    contents=json.loads(contents)['data']['list']
    data = []

    for li in contents:
        name = li.get('titleName')
        uuid = li.get('uuid')
        href='http://www.whszfcg.com/wuhan/views/announce/announce_info.html?uuid={uuid}&type=1'.format(uuid=uuid)
        ggstart_time = li.get('inputDate')

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//body/pre[string-length()>50]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//body/pre[contains(string(),"count")]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total =re.findall('"allcount":(\d+),',driver.page_source)[0]

    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="czyhome_centers"][string-length()>50]')

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
    div = soup.find('div', class_="czyhome_centers")
    return div


data = [

    ["zfcg_zhaobiao_gg", "http://www.whszfcg.com/wuhan/announce/editQueryMore?type=1&info=0&pageNo=1&pageSize=10", ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.whszfcg.com/wuhan/announce/editQueryMore?type=1&info=1&pageNo=1&pageSize=10", ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["zfcg_biangeng_gg", "http://www.whszfcg.com/wuhan/announce/editQueryMore?type=1&info=2&pageNo=1&pageSize=10", ["name", "ggstart_time", "href", 'info'],f1, f2],
    ["zfcg_liubiao_gg", "http://www.whszfcg.com/wuhan/announce/editQueryMore?type=1&info=3&pageNo=1&pageSize=10", ["name", "ggstart_time", "href", 'info'],f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省武汉市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':

    conp = ["postgres", "since2015", "192.168.3.171", "lch", "hubei_wuhan2"]
    work(conp=conp,num=1,total=3,headless=False)