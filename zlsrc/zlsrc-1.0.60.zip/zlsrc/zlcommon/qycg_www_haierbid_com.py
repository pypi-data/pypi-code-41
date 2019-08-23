import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large





def yc(f):
    def wrap(*krg):
        driver = krg[0]
        url = driver.current_url
        if 'k=f86Jg1QShHaBcO1JMrNQ4Xx8NGlgs79WNK0h20x4ZvOUh%2bkEwpVtnnlr46KENNFt' not in url:
            driver.find_element_by_link_text('采购预告').click()
            locator = (By.XPATH, "//ul[@class='breadcrumb']/li[@class='active'][contains(string(), '采购预告')]")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap


def zb(f):
    def wrap(*krg):
        driver = krg[0]
        url = driver.current_url
        if 'k=f86Jg1QShHbtYvbKo2qSTD2uS3tfl%2fdX0sa8uDTd00LFbk3pjvAYtuYjflehnfB6' not in url:
            driver.find_element_by_link_text('采购公告').click()
            locator = (By.XPATH, "//ul[@class='breadcrumb']/li[@class='active'][contains(string(), '采购公告')]")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

        return f(*krg)
    return wrap


def bg(f):
    def wrap(*krg):
        driver = krg[0]
        url = driver.current_url
        if 'k=f86Jg1QShHaeWOfo6kk49Ry7e1fQhKe9P48hcuubDB7%2fv1mVzq3uV7aHV790PjJ2' not in url:
            driver.find_element_by_link_text('变更公告').click()
            locator = (By.XPATH, "//ul[@class='breadcrumb']/li[@class='active'][contains(string(), '变更公告')]")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

        return f(*krg)
    return wrap


def zhongb(f):
    def wrap(*krg):
        driver = krg[0]
        url = driver.current_url
        if 'k=f86Jg1QShHb21wQ8JF6YwT2uS3tfl%2fdX0sa8uDTd00LFbk3pjvAYtuYjflehnfB6' not in url:
            driver.find_element_by_link_text('中标公告').click()
            locator = (By.XPATH, "//ul[@class='breadcrumb']/li[@class='active'][contains(string(), '中标公告')]")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='news-list unlist']/li[last()]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//span[@id='span1']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', total_page)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='news-list unlist']/li[last()]/a").get_attribute('href')[-40:]
        if 'page' not in url:
            s = '&id=%d' %num if num>1 else '&id=1'
            url+=s
        else:
            s = 'id=%d' % num if num > 1 else 'id=1'
            url=re.sub('id=[0-9]+',s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='news-list unlist']/li[last()]/a[not(contains(@href, '%s'))]"% val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    div = soup.find('ul', class_='news-list unlist')
    lis = div.find_all('li')
    data = []
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('span', class_='date').text.strip()
        link = a['href']
        if 'http' in link:
            href = link
        else:
            href = 'http://www.haierbid.com' + link
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='news-list unlist']/li[last()]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@id='span1']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', total_page)[0]
    driver.quit()
    return int(num)

def f3(driver, url):
    driver.get(url)

    if '该新闻必须是注册用户才能阅读' in str(driver.page_source):
        return 404
    locator = (By.XPATH, "//section[@id='divContent'][string-length()>40]")
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
    div = soup.find('section', id='divContent')
    return div


data = [
    ["qycg_yucai_gg",
     "http://www.haierbid.com",
     ["name", "ggstart_time", "href", "info"], yc(f1),yc(f2)],

    ["qycg_zhaobiao_gg",
     "http://www.haierbid.com",
     ["name", "ggstart_time", "href", "info"],zb(f1),zb(f2)],

    ["qycg_biangeng_gg",
     "http://www.haierbid.com",
     ["name", "ggstart_time", "href", "info"], bg(f1), bg(f2)],

    ["qycg_zhongbiao_gg",
     "http://www.haierbid.com",
     ["name", "ggstart_time", "href", "info"], zhongb(f1), zhongb(f2)],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="海尔招标网", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_haierbid_com"])
    # # chrome_option = webdriver.ChromeOptions()
    # # # chrome_option.add_argument('--headless')
    # # chrome_option.add_argument('--no-sandbox')
    # # chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # from selenium.webdriver import Chrome, ChromeOptions
    # for d in data[2:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = d[-1](driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=d[-2](driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


