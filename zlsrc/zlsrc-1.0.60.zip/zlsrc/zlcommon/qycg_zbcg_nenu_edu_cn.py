import json
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large



def f1(driver, num):
    locator = (By.XPATH, "//table[@id='GridView_Content']/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//td[contains(@id, 'fanye')]")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', txt)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='GridView_Content']/tbody/tr[last()]/td/a").get_attribute('href')[-30:]
        driver.find_element_by_xpath("//input[@class='defaultInputStyle']").clear()
        driver.find_element_by_xpath("//input[@class='defaultInputStyle']").send_keys(num)
        driver.find_element_by_xpath("//input[@class='defaultButtonStyle']").click()
        locator = (By.XPATH, "//table[@id='GridView_Content']/tbody/tr[last()]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", id='GridView_Content').tbody

    lis = div.find_all('tr', id=re.compile('line'))
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://zbcg.nenu.edu.cn/' + link
        info = {}
        span = li.find_all("td")[-2].text.strip()
        lx = li.find_all("td")[-1].text.strip()
        info['lx']=lx
        if re.findall(r'^\[(.*?)\]', title):
            zblx = re.findall(r'^\[(.*?)\]', title)[0]
            info['zblx'] = zblx
        if info:info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@id='GridView_Content']/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[contains(@id, 'fanye')]")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', txt)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='article'][string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('div', id='containerbody')
    return div


data = [

    #
    ["qycg_zhaobiao_gg",
     "http://zbcg.nenu.edu.cn/tylist.jsp?urltype=tree.TreeTempUrl&wbtreeid=1014",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    #
    ["qycg_zhongbiao_gg",
     "http://zbcg.nenu.edu.cn/tylist.jsp?urltype=tree.TreeTempUrl&wbtreeid=1015",
     ["name", "ggstart_time", "href", "info"],f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="东北师范大学政府采购", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "zbcg_nenu_edu_cn"])

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
    #     df=f1(driver, 11)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


