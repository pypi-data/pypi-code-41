import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large



def nmg_zb(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@class='table tab_one']/tbody/tr[last()]//a[@class='quanbu']")
        ggxz = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        if '正常公告' not in ggxz:
            driver.execute_script("changeParam('noticeNature','1')")
            locator = (By.XPATH, "//table[@class='table tab_one']/tbody/tr[last()]//a[@class='quanbu'][contains(string(), '正常公告')]")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

        return f(*krg)
    return wrap


def nmg_bg(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@class='table tab_one']/tbody/tr[last()]//a[@class='quanbu']")
        ggxz = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text.strip()
        if '更正公告' not in ggxz:
            driver.execute_script("changeParam('noticeNature','2')")
            locator = (By.XPATH,
                       "//table[@class='table tab_one']/tbody/tr[last()]//a[@class='quanbu'][contains(string(), '更正公告')]")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='table table-striped tab_two']/tbody/tr[last()]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    locator = (By.XPATH, "//span[@class='layui-laypage-curr']")
    snum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(snum)
    #
    if num != cnum:
        val = driver.find_element_by_xpath("//table[@class='table table-striped tab_two']/tbody/tr[last()]//a").get_attribute('href')[-12:]
        driver.execute_script('search({})'.format(num))

        locator = (By.XPATH, "//table[@class='table table-striped tab_two']/tbody/tr[last()]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_=re.compile('table-striped')).tbody
    lis = table.find_all('tr')
    for tr in lis[1:]:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('td')[-1].text.strip()
        onclick = a['href']
        href = 'http://www.nmgztb.com.cn'+onclick
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@class='table table-striped tab_two']/tbody/tr[last()]//a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//a[@class='layui-laypage-last']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(total_page)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@class, 'maincon')][string-length()>40]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='maincon')
    return div


data = [
    ["jqita_zhaobiao_gg",
     "http://www.nmgztb.com.cn/open-infos?infoType=11",
     ["name", "ggstart_time", "href", "info"],nmg_zb(f1),nmg_zb(f2)],

    ["jqita_biangeng_gg",
     "http://www.nmgztb.com.cn/open-infos?infoType=11",
     ["name", "ggstart_time", "href", "info"], nmg_bg(f1), nmg_bg(f2)],

    ["zfcg_zhongbiaohx_gg",
     "http://www.nmgztb.com.cn/open-infos?infoType=15",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.nmgztb.com.cn/open-infos?infoType=12",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

##该代码与内蒙古_neimenggusheng_1_ggzy 互相补充

def work(conp, **args):
    est_meta_large(conp, data=data, diqu="内蒙古自治区", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "neimenggu"])


    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = nmg_bg(f2)(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=nmg_bg(f1)(driver, 5)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


