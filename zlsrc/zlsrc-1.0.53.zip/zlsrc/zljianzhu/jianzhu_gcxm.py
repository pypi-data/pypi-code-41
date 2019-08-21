# encoding:utf-8
import json
import os
from multiprocessing import Semaphore
import pandas as pd
from bs4 import BeautifulSoup
from zlsrc.zljianzhu.scrap.jianzhu_etl import jianzhu_gcxm_est_html
from selenium import webdriver


sema = Semaphore(1)

# ---------------------------------------------------------程序主入口------------------------------------------------------

def f81(driver, arr,proxies,conp):
    href = arr[0]
    gcxm = arr[1]
    if (gcxm == '暂未查询到已登记入库信息') or (gcxm == 'None'):
        col = ["href", "gcxm", "xmxx_name", "xmxx_href", "xm_id", "xm_name", "xm_diqu", "xm_type", "qy_name"]
        return pd.DataFrame(columns=col)
    try:
        gcxm_list = [k['trs'] for k in (json.loads(w) for w in json.loads(gcxm))]
        datas = []
        for trs in gcxm_list:
            dat = get_gcxm(driver, href, trs)
            if dat:
                datas.append(dat)
        data = []
        for d in datas:
            data += d
    except ValueError:
        data = get_gcxm(driver, href, gcxm)
    df = pd.DataFrame(data=data)
    return df


# -------------------------------------------------多线程获取人员基本信息—---------------------------------------------------


def get_gcxm(driver, href, gcxm):
    div = BeautifulSoup(gcxm, 'html.parser')
    # 获取注册人员等详细信息
    ul = div.find('table', class_='pro_table_box pro_table_borderright').tbody
    trs = ul.find_all('tr')
    lis = []
    for tr in trs:
        if tr.find('div', class_='clearfix'):
            continue
        td = tr.find('td', attrs={"data-header": "项目名称"})
        try:
            a = td.find('a')
            xmxx_name = td.find('a').text.strip()
        except:
            print('数据错误！')
            continue
        xmxx_href = 'http://jzsc.mohurd.gov.cn' + a['onclick'].split("'")[1].replace("'", '')
        xm_id = tr.find('td', attrs={"data-header": "项目编码"})
        if xm_id:xm_id=xm_id.text.strip()
        else:xm_id=None
        xm_diqu = tr.find('td', attrs={"data-header": "项目属地"})
        if xm_diqu:xm_diqu=xm_diqu.text.strip()
        else:xm_diqu=None
        xm_type = tr.find('td', attrs={"data-header": "项目类别"})
        if xm_type:xm_type = xm_type.text.strip()
        else:xm_type = None
        qy_name = tr.find('td', attrs={"data-header": "建设单位"})
        if qy_name:qy_name = qy_name.text.strip()
        else:qy_name = None

        tmp = [href, gcxm, xmxx_name, xmxx_href, xm_id, xm_diqu, xm_type, qy_name]
        lis.append(tmp)
    return lis


dd = ["href", "gcxm", "xmxx_name", "xmxx_href", "xm_id", "xm_diqu", "xm_type", "qy_name"]

def work(conp, **args):
    jianzhu_gcxm_est_html(conp, f=f81, data=dd, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jianzhu"], pageloadtimeout=180, num=20)

