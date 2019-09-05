#coding:utf-8
import psutil
import datetime
import time
import platform
import subprocess
import socket
import uuid
from urllib import request
from tools import md5


class GethardWare:
    _sys="Windows"
    def __init__(self):
        self._sys = platform.system()

    #获取操作系统当前时间
    def get_nowdatetime(self):
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return now_time

    #查看CPU物理个数和使用率
    def get_cpucount(self):
        cpu_count=psutil.cpu_count(logical=False)
        #r_vcpucount="物理CPU个数: %s" % cpu_count
        cpu = (str(psutil.cpu_percent(1))) + '%'
        #r_cpu="cup使用率: %s" % cpu
        r_vlue={"r_vcpucount":cpu_count,"r_cpu":cpu}
        return r_vlue

    #查看内存信息,剩余内存.free  总共.total
    def get_ram(self):
        free=str(round(psutil.virtual_memory().free/(1024.0*1024.0*1024.0),2))  #剩余物理内存
        total=str(round(psutil.virtual_memory().total/(1024.0*1024.0*1024.0),2))  #物理内存
        memory = int(psutil.virtual_memory().total - psutil.virtual_memory().free) / float(
            psutil.virtual_memory().total)
        r_total="%s G" % total
        r_free="%s G" % free
        r_memory="%s %%" % int(memory * 100)
        r_value={"r_total":r_total,"r_free":r_free,"r_memory":r_memory}
        return r_value

    # 系统启动时间和系统用户
    def get_sysstarttimeandusers(self):
        sys_starttime=datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S") #系统时间
        users_count = len(psutil.users()) #用户个数
        users_list = ",".join([u.name for u in psutil.users()]) #用户列表
        #r_sys_starttime="系统启动时间: %s" % sys_starttime
        #r_users="当前有%s个用户，分别是 %s" % (users_count, users_list)
        r_value={"r_sys_starttime":sys_starttime,"r_users":users_list,"r_usercount":users_count}
        return r_value

    # 网卡，当前链接的流量等信息
    def get_netcard(self):
        netcard_info = []
        net = psutil.net_io_counters()
        bytes_sent = '{0:.2f} Mb'.format(net.bytes_recv / 1024 / 1024)
        bytes_rcvd = '{0:.2f} Mb'.format(net.bytes_sent / 1024 / 1024)
        #r_bytes="网卡接收流量 %s 网卡发送流量 %s" % (bytes_rcvd, bytes_sent)
        netcard_info.append(('rcvd_bytes',bytes_rcvd)) #网卡接收流量
        netcard_info.append(('sent_bytes',bytes_sent)) #网卡发送流量
        return netcard_info

    #IP地址获取，内网IP和外网IP,mac地址
    def get_ipAndMac(self):
        ipmac=[]
        # IP地址获取，内网IP和外网IP
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        try:
            res = request.urlopen('http://pv.sohu.com/cityjson')
            request_info = res.read().decode('gbk')
            gw_ip = str(request_info).split('=')[1].split(',')[0].split('"')[3]  # 外网IP
        except Exception as e:
            gw_ip=''
        ipmac.append(('local_ip', ip))  # 本机内网IP
        ipmac.append(('gw_ip', gw_ip))  # 外网IP
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        n_mac=":".join([mac[e:e + 2] for e in range(0, 11, 2)])
        print(n_mac)
        ipmac.append(('macaddress', n_mac))
        return ipmac

    #磁盘信息
    def get_disk(self):
        r_disk=[]
        io = psutil.disk_partitions()
        print(io)
        for i in io:
            try:
                disk_name=str(i.device).split(':')[0]+"盘符"
                o = psutil.disk_usage(i.device)
                r_total=str(int(o.total / (1024.0 * 1024.0 * 1024.0))) + "G"  #"总容量：" + str(int(o.total / (1024.0 * 1024.0 * 1024.0))) + "G"
                r_used=str(int(o.used / (1024.0 * 1024.0 * 1024.0))) + "G"    #"已用容量：" + str(int(o.used / (1024.0 * 1024.0 * 1024.0))) + "G"
                r_free=str(int(o.free / (1024.0 * 1024.0 * 1024.0))) + "G"    #"可用容量：" + str(int(o.free / (1024.0 * 1024.0 * 1024.0))) + "G"
                r_disk.append((str(disk_name),(r_total,r_used,r_free)))
            except:
                continue

        return r_disk

    #mac系统获取序列号
    def get_macos(self):
        process = subprocess.Popen("ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformSerialNumber/ { print $3; }'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        command_output = process.stdout.read().decode('utf-8')
        print(command_output)
        return str(command_output).replace('"','').replace('\n','').strip()


    #windows系统获取cpu的信息加磁盘序列号
    def get_wincpuid(self):
        process=subprocess.Popen("wmic cpu get ProcessorId", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        command_output = process.stdout.read()
        result =  str(command_output,'ascii')
        if result and len(result)>11:
            if "ERROR" in result:
                print(-1, "获取CPU地址失败")
            cpuid=result[11:].strip()
        else:
            cpuid=''
        process = subprocess.Popen("wmic DISKDRIVE get SerialNumber /value", shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        command_output = process.stdout.read()
        result =  str(command_output,'ascii').replace('\r','').replace('\n','').replace(' ','')
        try:
            # disknid=result.split('=')[1]
            disknid = result.split('SerialNumber=')[1]
        except Exception as e:
            disknid=""
        if not disknid:
            mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
            n_mac = ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
        else:
            n_mac = ""
        return cpuid+disknid+ n_mac

    #根据不同操作系统获取唯一标识
    def get_cpuidOrSerialNumber(self):
        try:
            onlyNum = ''
            sys = self._sys
            if sys == "Windows":
                onlyNum = self.get_wincpuid()
            elif sys == "Darwin":
                onlyNum = self.get_macos()

            # MD5加密
            onlyNum = md5.genearteMD5(onlyNum)
            return onlyNum
        except Exception as e:
            raise e


        #调用测试
if __name__ == "__main__":
    ghw=GethardWare()


    #操作系统
    sys=ghw._sys
    if sys=="Windows":
        print(ghw.get_wincpuid())
        print("当前操作系统是："+sys)
    elif sys=="Darwin":
        print("当前操作系统是：Mac")
        print(ghw.get_macos())
    elif sys=="Linux":
        print("当前操作系统是："+sys)
    print('')
    print(ghw.get_nowdatetime()) #系统当前时间
    print('')

    #获取CPU信息
    cpus=ghw.get_cpucount()
    for k,v in cpus.items():
        print(v)

    print('')

    #查看内存信息
    rams=ghw.get_ram()
    for k1,v1 in rams.items():
        print(str(k1)+":"+str(v1))

    print('')

    #系统启动时间和用户
    users_time=ghw.get_sysstarttimeandusers()
    for k2,v2 in users_time.items():
        print(v2)

    print('')

    #网卡信息
    netcards=ghw.get_netcard()
    for k3,v3 in netcards:
        print(v3)

    print('')

    #磁盘信息
    diskinfo=ghw.get_disk()
    for k4,v4 in diskinfo:
        print(k4+'\n')
        for i in range(len(v4)):
            print(str(v4[i])+'\n')







