import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import add_info,est_meta,est_html,est_tbs,est_meta_large



def f1_data(driver, num):
    locator = (By.XPATH, "//div[@class='r_list']/dl[last()]/dt/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page_total = driver.find_element_by_xpath("//div[@class='pages']").text.strip()
    cnum = int(re.findall(r'(\d+)/', page_total)[0])
    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='r_list']/dl[last()]/dt/a").get_attribute('href')[-30:]
        url = driver.current_url
        s = 'page=%d' % num if num > 1 else 'page=1'
        url = re.sub('page=[0-9]+?', s, url)
        driver.get(url)
        time.sleep(1)
        locator = (By.XPATH, "//div[@class='r_list']/dl[last()]/dt/a[not(contains(@href, '%s'))]"% val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    data = []
    driver.execute_script('window.scrollBy(0,1400)')
    # print(1111111)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='r_list')
    dls = div.find_all('dl')
    for tr in dls:
        a = tr.dt.find('a')
        try:
            name = a['title'].strip()
        except:
            name = a.text.strip()
        ggstart_time = tr.find('dd', class_='trt_js_tit4').span.text.strip()
        href = a['href']
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f1(driver, num):
    url = driver.current_url
    if 'channelid=222788' in url:
        df = f1_data(driver, num)
        return df
    locator = (By.XPATH, "//ul[@class='list']/li[last()]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    pre = driver.find_element_by_xpath("//div[@class='page mt20']/font[last()]").text.strip()
    cnum = int(re.findall(r'(\d+)', pre)[0])
    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='list']/li[last()]/a").get_attribute('href')[-20:]
        if 'index' not in url:
            s = 'index_%d.htm' % (num-1) if num>1 else 'index.htm'
            url += s
        elif num == 1:
            url = re.sub('index_[0-9]+', 'index.htm', url)
        else:
            s = 'index_%d.htm' % (num-1) if num > 1 else 'index.htm'
            url = re.sub('index_[0-9]+', s, url)
        driver.get(url)
        time.sleep(1)
        locator = (By.XPATH, "//ul[@class='list']/li[last()]/a[not(contains(@href, '%s'))]"% val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find('ul', class_='list')
    dls = ul.find_all('li')
    for tr in dls:
        a = tr.find('a')
        try:
            name = a['title'].strip()
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span').text.strip()
        href = url.rsplit('/', maxsplit=1)[0]+a['href'].split('.', maxsplit=1)[1]
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    url = driver.current_url
    if 'channelid=222788' in url:
        locator = (By.XPATH, "//div[@class='r_list']/dl[last()]/dt/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page_total = driver.find_element_by_xpath("//div[@class='pages']").text.strip()
        num = re.findall(r'总页数:(\d+)', page_total)[0]
        return int(num)

    locator = (By.XPATH, "//ul[@class='list']/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    pre = driver.find_element_by_xpath("//div[@class='page mt20']/font[last()-1]").text.strip()
    num = re.findall(r'总共(\d+)页', pre)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='xlcontent'][string-length()>100]")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
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
    div = soup.find('div', class_='xlcontent')
    return div


data = [
    ["zfcg_zhaobiao_shiji_gg",
     "http://www.zfcg.sz.gov.cn/cggg/cgggsj/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'diqu':'市级'}),f2],

    ["zfcg_zhaobiao_quji_gg",
     "http://www.zfcg.sz.gov.cn/cggg/cgggqj/",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'diqu':'区级'}),f2],

    ["zfcg_zhongbiao_shiji_gg",
     "http://www.zfcg.sz.gov.cn/cggg/zbcjggsj/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'市级'}), f2],

    ["zfcg_zhongbiao_quji_gg",
     "http://www.zfcg.sz.gov.cn/cggg/zbcjggqj/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'区级'}), f2],
###
    ["zfcg_zhaobiao_shiji_quan_gg",
     "http://61.144.227.212/was5/web/search?page=1&channelid=222788&searchword=ctype%3D%E5%B8%82%E7%BA%A7%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&keyword=ctype%3D%E5%B8%82%E7%BA%A7%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&perpage=10&outlinepage=5&searchscope=&timescope=&timescopecolumn=&orderby=-DOCRELTIME&chnlid=&andsen=&total=&orsen=&exclude=",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'diqu':'市级'}),f2],

    ["zfcg_zhaobiao_quji_quan_gg",
     "http://61.144.227.212/was5/web/search?page=1&channelid=222788&searchword=ctype%3D%E5%8C%BA%E7%BA%A7%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&keyword=ctype%3D%E5%8C%BA%E7%BA%A7%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A&perpage=10&outlinepage=5&searchscope=&timescope=&timescopecolumn=&orderby=-DOCRELTIME&chnlid=&andsen=&total=&orsen=&exclude=",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'diqu':'区级'}),f2],

    ["zfcg_zhongbiao_shiji_quan_gg",
     "http://61.144.227.212/was5/web/search?page=1&channelid=222788&searchword=ctype%3D%E5%B8%82%E7%BA%A7%E4%B8%AD%E6%A0%87%E6%88%90%E4%BA%A4%E5%85%AC%E5%91%8A&keyword=ctype%3D%E5%B8%82%E7%BA%A7%E4%B8%AD%E6%A0%87%E6%88%90%E4%BA%A4%E5%85%AC%E5%91%8A&perpage=10&outlinepage=5&searchscope=&timescope=&timescopecolumn=&orderby=-DOCRELTIME&chnlid=&andsen=&total=&orsen=&exclude=",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'市级'}), f2],

    ["zfcg_zhongbiao_quji_quan_gg",
     "http://61.144.227.212/was5/web/search?page=1&channelid=222788&searchword=ctype%3D%E5%8C%BA%E7%BA%A7%E4%B8%AD%E6%A0%87%E6%88%90%E4%BA%A4%E5%85%AC%E5%91%8A&keyword=ctype%3D%E5%8C%BA%E7%BA%A7%E4%B8%AD%E6%A0%87%E6%88%90%E4%BA%A4%E5%85%AC%E5%91%8A&perpage=10&outlinepage=5&searchscope=&timescope=&timescopecolumn=&orderby=-DOCRELTIME&chnlid=&andsen=&total=&orsen=&exclude=",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'区级'}), f2],
]


### 深圳市政府采购监管网

### 深圳政府在线

def work(conp,**args):
    est_meta_large(conp,data=data,diqu="广东省深圳市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlsrc","shenzhenshi"])
    #
    # for d in data[5:]:
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

