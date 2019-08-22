import datetime
import random
import re
import time
import traceback
from threading import Semaphore
import requests
from lmf.dbv2 import db_command, db_query
from zlsrc.util.fake_useragent import UserAgent


class Ips:
    def __init__(self):
        self.ua = UserAgent()
        self.add_ip_flag = False
        self.sema = Semaphore(1)
        self.long_ip_url = ""
        self.long_ip_conp = ["postgres", "since2015", "192.168.3.171", "postgres", "public"]
        self.long_ip_num = 20


    def select_long_ip(self, long_ip_conp):
        sql1 = """
        select ip,ExpireTime from %s.long_ip_cfg;
        """ % (long_ip_conp[4])
        df = db_query(sql1, dbtype="postgresql", conp=long_ip_conp)
        if df.values.tolist():
            data = df.sample(frac=1).values.tolist()
        else:
            data = df.values.tolist()
        return data

    def insert_long_ip(self, long_ip_conp, ip, ExpireTime):
        sql1 = """
        insert into %s.long_ip_cfg(ip, ExpireTime,create_time) values ('%s', '%s',now());
        """ % (long_ip_conp[4], ip, ExpireTime)
        db_command(sql1, dbtype="postgresql", conp=long_ip_conp)


    def delete_long_ip(self, long_ip_conp, ip):
        sql1 = """
        delete from %s.long_ip_cfg where ip='%s';
        """ % (long_ip_conp[4], ip)
        db_command(sql1, dbtype="postgresql", conp=long_ip_conp)


    # 入口
    def get_long_ips(self):
        long_ip_num = int(self.long_ip_num)
        long_ip_url = self.long_ip_url
        long_ip_conp = self.long_ip_conp
        # 获取数据库中的IP
        data = self.select_long_ip(long_ip_conp)
        if data:
            len_data = int(len(data))
        else:
            len_data = 0
        # print(len_data, 'len_data', long_ip_num, 'conp', long_ip_conp)
        print("数据库中有 {} 条长效IP".format(len_data))
        if len_data < long_ip_num:
            # 数据库没有IP,插入IP
            print("准备插入长效 {} 个IP".format(long_ip_num - len_data))
            i = 5
            while (long_ip_num - len_data) > 0 and i > 0:
                ip, ExpireTime = self.get_long_ip(long_ip_url)
                # print(ip, ExpireTime)
                if ip:
                    # 插入数据库
                    self.insert_long_ip(long_ip_conp, ip, ExpireTime)
                else:
                    i -= 1
                    continue
                long_ip_num -= 1
            if i != 5:print("{} 个长效IP插入失败".format(5-i))
            else:print("长效IP全部插入成功！")
        else:
            de_num,up_num = 0, 0
            for d in data:
                d_ip, d_ExpireTime = d[0], d[1]
                # 获取当前时间
                end_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
                d1 = datetime.datetime.strptime('{}'.format(d_ExpireTime), '%Y-%m-%d %H:%M:%S')
                d2 = datetime.datetime.strptime('{}'.format(end_time), '%Y-%m-%d %H:%M:%S')
                # # 比较时间差值
                delta = d1 - d2
                if delta.days < 0:
                    # ip失效，替换新ip
                    # 先删除失效ip
                    self.delete_long_ip(long_ip_conp, d_ip)
                    de_num += 1
                    # 再获取ip
                    t,i = 1,5
                    while t > 0 and i>0:
                        ip, ExpireTime = self.get_long_ip(long_ip_url)
                        if ip:
                            # 插入数据库
                            self.insert_long_ip(long_ip_conp, ip, ExpireTime)
                            up_num += 1
                        else:
                            i-=1
                            continue
                        t -= 1

            if de_num != 0:print("删除失效IP {} 个".format(de_num))
            if up_num != 0: print("更新长效IP {} 个".format(up_num))


    def get_long_ip(self, long_ip_url):
        self.sema.acquire()
        i = 3
        try:
            url = long_ip_url
            r = requests.get(url, timeout=40, headers={'User-Agent': self.ua.random}).json()
            # r = {'msg': '', 'data': [{'IP': '49.73.170.9449:43562', 'ExpireTime': '2019-08-09 14:33:18'}], 'success': 'true', 'code': 0}
            time.sleep(1)
            ip = r['data'][0]['IP']
            ExpireTime = r['data'][0]['ExpireTime']
            while re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None and i > 0:
                time.sleep(3 - i)
                i -= 1
                url = long_ip_url
                r = requests.get(url, timeout=40, headers={'User-Agent': self.ua.random}).json()
                # r = {'msg': '', 'data': [
                #     {'IP': '113.143.56.{}:1560'.format(random.randint(0, 255)), 'ExpireTime': '2019-08-13 14:43:31'}],
                #      'success': 'true', 'code': 0}
                time.sleep(1)
                ip = r['data'][0]['IP']
                ExpireTime = r['data'][0]['ExpireTime']
        except:
            ip = False
            traceback.print_exc()
            ExpireTime = False
        finally:
            self.sema.release()
            if ip:
                if '登录IP不是白名单IP，请在用户中心添加该白名单' in ip:
                    self.add_ip_flag = True
                    self.add_ip()
                    self.get_long_ip(long_ip_url)

        print(ip,ExpireTime)
        return ip, ExpireTime


    def add_ip(self):
        # 获取本机ip，是否在白名单中
        if not self.add_ip_flag:
            print('[Info]:不执行添加本地ip到白名单的操作。')
        else:
            try:
                try:
                    r = requests.get("http://www.trackip.net/", timeout=10, headers={'User-Agent': self.ua.random}).text

                except:
                    r = requests.get("http://200019.ip138.com/", timeout=10,
                                     headers={'User-Agent': self.ua.random}).text
                ip = r[r.find('title') + 6:r.find('/title') - 1]
                ip = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
                i = 3
                while ip == []:
                    try:
                        r = requests.get("http://www.trackip.net/", timeout=10,
                                         headers={'User-Agent': self.ua.random}).text
                    except:
                        r = requests.get("http://200019.ip138.com/", timeout=10,
                                         headers={'User-Agent': self.ua.random}).text
                    ip = r[r.find('title') + 6:r.find('/title') - 1]
                    ip = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
                    i -= 1
                    if i < 0: break
                ip = ip[0]
                i = 3
                ips = None
                while i > 0:
                    x = """http://http.zhiliandaili.cn/Users-whiteIpListNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc"""
                    r = requests.get(x, timeout=40, headers={'User-Agent': self.ua.random}).json()

                    if "data" in r.keys():
                        ips = r["data"]
                        print('ips', ips)
                        break
                    else:
                        time.sleep(1)
                        i -= 1
                if ips == None:
                    return False
                if ip in ips:
                    print("%s 已经在白名单中" % ip)
                    return True
                i = 3

                while i > 0:
                    x = """http://http.zhiliandaili.cn/Users-whiteIpAddNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc&whiteip=%s""" % ip
                    r = requests.get(x, timeout=40, headers={'User-Agent': self.ua.random}).json()
                    if "存在" in r["msg"]:
                        print("IP : [ %s ] 已经在白名单中" % ip)
                        break
                    if "最多数量" in r["msg"]:
                        time.sleep(1)
                        x = """http://http.zhiliandaili.cn/Users-whiteIpAddNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc&whiteip=%s&index=5""" % ip
                        r = requests.get(x, timeout=40, headers={'User-Agent': self.ua.random}).json()

                    if "成功" in r["msg"]:
                        print("添加 IP %s" % ip)
                        break
                    i -= 1
                    time.sleep(1)
                self.add_ip_flag = False
            except:
                traceback.print_exc()


    def write(self, **krg):
        """
        :param krg:
        add_ip_flag : 是否添加本地ip到白名单     默认值 True
        long_ip_conp: 存放长效IP的数据库,分阿里云以及昆明环境，  默认为["postgres", "since2015", "192.168.3.171", "postgres", "public"]
        long_ip_url: 获取长效IP的链接
        long_ip_num: 获取长效IP的个数   默认值 20
        :return:
        """
        if "add_ip_flag" not in krg.keys():
            self.add_ip_flag = True
        else:
            self.add_ip_flag = krg["add_ip_flag"]

        if krg.get("loc")=="ailiyun":
            self.long_ip_conp = ["postgres", "since2015", "192.168.4.201", "postgres", "public"]
        elif krg.get("loc") == "kunming":
            self.long_ip_conp = ["postgres", "since2015", "192.168.169.89", "postgres", "public"]
        else:
            self.long_ip_conp = ["postgres", "since2015", "192.168.3.171", "postgres", "public"]

        if "long_ip_url" not in krg.keys():
            self.long_ip_url = ""
        else:
            self.long_ip_url = krg["long_ip_url"]

        if "long_ip_num" not in krg.keys():
            self.long_ip_num = 20
        else:
            self.long_ip_num = krg["long_ip_num"]
        # 开始
        self.get_long_ips()




def work(**args):
    m = Ips()
    m.write(**args)



if __name__ == '__main__':
    long_ip_num= 20
    long_ip_url = ""
    long_ip_conp = ["postgres", "since2015", "192.168.3.171", "postgres", "public"]

    work(long_ip_num=long_ip_num,long_ip_url=long_ip_url,conp=long_ip_conp)