# coding:utf-8

import time
import os
import datetime
from datetime import timedelta
# import base64

from robot.api import logger
import win32api
import win32con
import win32serviceutil
import ntplib
from ntplib import NTPException

status_code = {
    
    0: "UNKNOWN",
    
    1: "STOPPED",
    
    2: "START_PENDING",
    
    3: "STOP_PENDING",
    
    4: "RUNNING"
    
}


class SysCon:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def start_service(self, service_name='GSUPService'):
        st = win32serviceutil.QueryServiceStatus(service_name)[1]
        if st == 4:
            print(('当前服务%s的状态为:%s' % (service_name, status_code[st])))
            pass
        elif st == 2:
            print(('当前服务%s 的状态为 %s' % (service_name, status_code[st])))
            pass
        elif st == 1:
            print(('当前服务%s 的状态为： %s，开始启动服务' % (service_name, status_code[st])))
            win32serviceutil.StartService(service_name)
            print("服务启动成功")
        else:
            print(('当前服务状态为：%s,需要手动启动' % status_code[st]))
            pass
    
    def restart_service(self, service_name='GSUPService'):
        st = win32serviceutil.QueryServiceStatus(service_name)[1]
        if st == 4:
            win32serviceutil.StopService(service_name)
            time.sleep(2)
            win32serviceutil.StartService(service_name)
        elif st == 1:
            win32serviceutil.StartService(service_name)
        else:
            print(('当前服务状态为：%s,需要手动启动' % status_code[st]))
            pass
    
    # 修改系统时间，以天/小时为单位
    def modify_sys_time_as_now(self, days=0, hours=0):
        """
        自定义系统时间，以天为单位
        :param days: 天
        :param hours: 小时
        :return:
        """
        global now, new_time
        now = datetime.datetime.now()
        if any([not isinstance(days, int), not isinstance(hours, int)]):
            raise TypeError("The type of days or hours param must be int !")
        if any([days != 0, hours != 0]):
            new_time = now + timedelta(days=days, hours=hours)
        elif all([days == 0, hours == 0]):
            new_time = now
        timetuple_ = new_time.timetuple()
        
        win32api.SetLocalTime(timetuple_)
    
    def run_program(self, pg, params="", fdir="", isAdmin=False):
        """
        windows 执行命令，并返回子进程的返回值
        :param pg: 要打开的程序
        :param params: 传递给要打开程序的参数，默认为空
        :param fdir: 执行程序所在的目录，如果已经在跟目录，默认为空
        :return:
        """
        global r
        import subprocess
        if fdir != '':
            pg = os.path.join(fdir, pg)
        if isAdmin:
            r = subprocess.Popen('sudo  %s %s' % (pg, params), stdout=subprocess.PIPE, shell=True)
        else:
            r = subprocess.Popen(['CMD', '/C', pg, params], stdout=subprocess.PIPE)
        
        return r.wait()
    
    def gdp_uninstall(self):
        """
        自动卸载GDP
        :return:
        """
        import subprocess
        try:
            version = RegFunc().get_gsup_verison()
        except ValueError:
            print("gdp已经卸载")
        else:
            gdp_path = fr'C:\Program Files (x86)\Common Files\Glodon Shared\GDP\{version}'
            
            for item in os.listdir(gdp_path):
                if item.endswith('.exe'):
                    global f_path
                    f_path = os.path.join(gdp_path, item)
                    break
            
            p = subprocess.Popen(f' "{f_path}" /VERYSILENT /NORESTART', stdout=subprocess.PIPE, shell=True)
            return_code = p.wait()
            if return_code == 0:
                print(('卸载GDP成功，卸载的版本为:%s' % version))
            else:
                raise Exception('卸载失败！')
    
    def gdp_update(self, service_name='gdpsvc'):
        """
        验证gdp服务升级
        :param service_name:
        :return:
        """
        print("《-----开始升级前GDP版本验证-----》")
        qrv = RegFunc()
        old_version = qrv.get_gsup_verison()
        print(("--->升级前版本为:{}".format(old_version)))
        print('----->gdp开始升级')
        self.restart_service(service_name=service_name)
        print('等待GDP服务升级中。。。。。。')
        sum_time = 0
        while qrv.get_gsup_verison() == old_version:
            time.sleep(1)
            sum_time += 1
            # logger.info("时间已过 %d 秒" % sum_time,also_console=True)
            if sum_time > 300:
                raise RuntimeError("！！等待了300秒GDP升级未成功,请检查！")
            if qrv.get_gsup_verison() != old_version:
                print(("--->升级后版本为：%s" % qrv.get_gsup_verison()))
                print(('-----> 升级成功,升级所用时间：%d 秒 <-----' % (sum_time,)))
                break
    
    def gdp_install(self, gdp_exe_path):
        """
        自动安装gdp,需要指定安装包路径。
        :param gdp_exe_path: 安装包路径
        :return:
        """
        import subprocess
        p = subprocess.Popen(' "%s" /SP- /VERYSILENT /NORESTART /SUPPRESSMSGBOXES' % gdp_exe_path,
                             stdout=subprocess.PIPE, shell=True)
        return_code = p.wait()
        if return_code == 0:
            version = RegFunc().get_gsup_verison()
            print(("安装后的版本为:%s" % version))
        else:
            raise Exception("安装未成功！！")
    
    def gdp_init(self, gdp_exe_path):
        import subprocess
        try:
            version = RegFunc().get_gsup_verison()
        except ValueError:
            self.gdp_install(gdp_exe_path)
        else:
            gdp_path = r'C:\Program Files (x86)\Common Files\Glodon Shared\GDP\{}'.format(version)
            
            for item in os.listdir(gdp_path):
                if item.endswith('.exe'):
                    global _f_path
                    _f_path = os.path.join(gdp_path, item)
                    break
            
            p = subprocess.Popen(' "{}" /VERYSILENT /NORESTART'.format(_f_path), stdout=subprocess.PIPE, shell=True)
            return_code = p.wait()
            if return_code == 0:
                print(('卸载GDP成功，卸载的版本为:%s' % version))
            else:
                raise Exception('卸载失败！')
            print('开始安装gdp。。。。')
            self.gdp_install(gdp_exe_path)
    
    def recover_sys_time(self):
        """
        恢复系统时间到当前时间
        :return:
        """
        ntpc = ntplib.NTPClient()
        try:
            response = ntpc.request('cn.pool.ntp.org')
        except NTPException:
            time.sleep(3)
            response = ntpc.request('tw.pool.ntp.org')
        ts = response.tx_time
        _date = time.strftime('%Y-%m-%d', time.localtime(ts))
        _time = time.strftime('%X', time.localtime(ts))
        os.system('date {0} && time {1}'.format(_date, _time))
        print("Recover System Time OK!")
    
    def get_pid(self, name):
        """
        获取进程的pid
        :param name:
        :return:
        """
        import psutil
        for i in psutil.pids():
            if psutil.Process(i).name() == name:
                return psutil.Process(i).pid
    
    def create_or_delete_ini_file(self, op_t):
        """
        :param op_t: 0---删除，1---创建
        :return:
        """
        if not isinstance(op_t, int):
            raise TypeError('The type of op_t must be int!')
        f_l = os.listdir(r'C:\\')
        d_l = [x for i, x in enumerate(f_l) if x.find('GTC_AUTOTEST') != -1]
        if op_t == 0:
            os.system('del /F /S /Q c:\\{}'.format(d_l[0])) if len(d_l) > 0 else logger.info(
                '当前目录文件下GTC_AUTOTEST* 已经删除')
        elif op_t == 1:
            os.system('type NUL > c:\\GTC_AUTOTEST_202D8433-3527-46D0-8BA7-DF3A2A215139.ini') if len(
                d_l) == 0 else logger.info(
                '当前目录文件下GTC_AUTOTEST* 已经存在')
    
    def verify_env(self, env='cs'):
        """切换 测试的环境"""
        if env == 'cs':
            self.create_or_delete_ini_file(1)
            logger.info('切换测试环境成功', also_console=True)
        elif env == 'sc':
            self.create_or_delete_ini_file(0)
            logger.info('切换生产环境成功', also_console=True)
        else:
            logger.error('env 赋值错误！')
            return
    
    def gcm_reg_modify(self, env='cs'):
        gcm_reg = RegFunc(sub_key=r'SOFTWARE\Wow6432Node\GrandSoft\GCM\2.0')
        
        def get_key():
            for i in range(win32api.RegQueryInfoKey(gcm_reg.handle)[1]):
                yield win32api.RegEnumValue(gcm_reg.handle, i)[0]
        
        if env == 'cs':
            if 'url' in [key for key in get_key()]:
                logger.info('当前为测试环境!', also_console=True)
            else:
                gcm_reg.reg_set_value('url', win32con.REG_SZ, 'cm-backup.glodon.com')
                logger.info('切换为测试环境！', also_console=True)
        elif env == 'sc':
            if 'url' in [key for key in get_key()]:
                win32api.RegDeleteValue(gcm_reg.handle, 'url')
                logger.info('切换为生产环境！', also_console=True)


class RegFunc(object):
    """
    获取注册表相关属性
    """
    
    def __init__(self, key=win32con.HKEY_LOCAL_MACHINE, sub_key=r'Software\Wow6432Node\Glodon\GDP\2.0'):
        reg_flags = win32con.WRITE_OWNER | win32con.KEY_WOW64_64KEY | win32con.KEY_ALL_ACCESS
        self.handle = win32api.RegOpenKeyEx(key, sub_key, 0, reg_flags)
        self._sub_key = sub_key
    
    def get_guid(self):
        if self._sub_key == r'Software\Wow6432Node\Glodon\GDP\2.0':
            return win32api.RegQueryValueEx(self.handle, 'guid')[0]
        else:
            raise Exception('get deviceid wrong,please check sub_key!')
    
    def get_value(self, key):
        
        return win32api.RegQueryValueEx(self.handle, key)[0]
    
    def reg_delete_key(self, key):
        win32api.RegDeleteValue(self.handle, key)
    
    def get_gsup_verison(self):
        if self._sub_key == r'Software\Wow6432Node\Glodon\GDP\2.0':
            try:
                gdp_version = win32api.RegQueryValueEx(self.handle, 'Version')[0]
            except:
                raise ValueError('version 值不存在，请检查是否安装！')
            return gdp_version
        else:
            raise Exception('get gsup version wrong,please check sub_key!')
    
    def reg_set_value(self, key_name, d_type, key_value):
        """

        :param handle: 要修改或者新增key的父键
        :param key_name: 要修改或者新增key的名称
        :param d_type: key的数据类型，具体可查看win32con.REG_**系列
        :param key_value: key的值
        :return:
        """
        try:
            win32api.RegSetValueEx(self.handle, key_name, 0, d_type, key_value)
        except WindowsError as e:
            raise e
        except OSError as e:
            raise e
        except SystemError as e:
            raise e


if __name__ == '__main__':
    pass
