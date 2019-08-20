import socket, os, sys, requests, json
import uuid, re
import subprocess
from crontab import CronTab
import requests, json

host_ip = ''
host_name = ''
host_mac = ''
names = []
macs = []
all_jsons = {}
check_version = 0
dirname = os.path.dirname(__file__)


def test():
    global dirname
    path = dirname + "/data/file.txt"
    f = open(path, "w")
    f.write("ok")
    print("doneit")
    f.close()


def ethtool_x_cp():
    global dirname
    path = dirname + "/data/ethtoolpyth.py"
    # f = open(path, "w")
    # f.write("import subprocess\n\r")
    # f.write("import time\n\r")
    # f.write("print('Running ethtool command')\n\r")
    # f.write("subprocess.call(['sudo', 'ethtool', '-s','enp1s0', 'wol','g' ])\n\r")
    # f.write("time.sleep(10)\n\r")
    # f.write("subprocess.call(['sudo', 'ethtool', '-s','enp1s0', 'wol','g' ])\n\r")
    # f.close()

    try:
        subprocess.call(["sudo", "chmod", "a+x", path])
        print("Adding ethtoolpyth.py")
        print("yes or no")
        subprocess.call(["sudo", "cp", "-i", path, "/bin"])

    except:
        print(" Error while adding file to bin")


def cron_jobs():
    global check_version
    global dirname
    try:
        print("Running cron command")
        cron = CronTab(user='root')

        print("root access gained")

        for jobs in cron:
            print(jobs)
            if jobs.comment == 'run_it' or jobs.comment == 'daily_run':
                cron.remove(jobs)
                cron.write()

        # **************** knowing python version **********************************
        __knowversion = ''
        if sys.version_info[0] < 3:
            check_version = 2
            __knowversion = 'python /bin/ethtoolpyth.py &'
        else:
            __knowversion = 'python3 /bin/ethtoolpyth.py &'
        # **************************************************************************

        # job = cron.new(command='python3 /bin/ethtoolpyth.py &', comment="run_it")
        job = cron.new(command=__knowversion, comment="run_it")
        job.every_reboot()
        cron.write()

        # cmd_run = dirname + '/daily.py &'
        # cmd_run = "python3 " + cmd_run
        # job2 = cron.new(command=cmd_run, comment='daily_run')
        # job2.minute.every(2)  # change it to hourly 888888880000000000000000000
        # cron.write()

        for jobs in cron:
            print(jobs)

    except Exception as ex:
        print("Unable to create in job{0} ----{1}".format(type(ex).__name__, ex.args))


def comp_info():
    try:
        global host_name
        global host_ip
        global host_mac
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        print("Hostname :  ", host_name)
        print("IP : ", host_ip)
        print("The MAC address : ")
        print(':'.join(re.findall('..', '%012x' % uuid.getnode())))
        host_mac = (':'.join(re.findall('..', '%012x' % uuid.getnode())))
    except:
        print("Unable to get Hostname and IP")


def tool_run():
    global dirname
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        ip_address_part = ip_address[0:11]
        ip_address_part += "1-"
        ip_address_part += ip_address[0:11]
        ip_address_part += "255"
        print(ip_address_part)
        s.close()
        print("Running Nbtscan ........")
        # subprocess.call(["nbtscan", ip_address_part])

        path = dirname + "/data/output.txt"
        f = open(path, "w")
        p = subprocess.check_output(["nbtscan", ip_address_part]).decode("utf-8")
        f.write(p)
        f.close()
    except:
        print("Nbt scan failed ( Please check internet is connected!)")

    try:
        path = dirname + "/data/output2.txt"
        f = open(path, "w")
        p2 = subprocess.check_output(["sudo", "arp-scan", ip_address_part]).decode("utf-8")
        f.write(p2)
        f.close()
    except:
        print("arp-scan failed ( Please check internet is connected!)")


def soft_install():
    try:
        print("installing ethtool")
        subprocess.call(["sudo", "apt-get", "install", "ethtool"])
        print("Ethtool installed")

    except:
        print("ethtool installation failed")

    try:
        print("Installing nbttool")
        subprocess.call(["sudo", "apt-get", "install", "nbtscan"])
        print("Nbtscan installed")

    except:
        print("ethtool installation failed")
    try:
        print("Installing arp-scan")
        subprocess.call(["sudo", "apt-get", "install", "arp-scan"])
        print("arp-scan installed")

    except:
        print("arp-scan installtion failed")


def checker(data, length=64):
    if len(data) <= 0 or len(data) > length:
        print("Not valid Input, length must be less than {0}".format(length))
        return True
    return False


def send_data():
    global names
    global macs
    global dirname
    try:
        for x in range(0, len(macs)):
            print("{0}---------{1}".format(names[x], macs[x]))

        jsondata = []
        for i in range(1, len(macs)):
            list = [names[i], macs[i]]
            jsondata.append(list)

        # for x in jsondata:
        #     print(x)

        # *****clubing****************************************************
        if check_version == 0:
            check = input("Do you want to update computer list yes or no  : ")
        else:
            check = raw_input("Do you want to update computer list yes or no  : ")

        if check == 'no':
            return 1

        print("")
        print(" - - - - - All inputs given are case sensitive! - - - - - - - - - ")
        print("")

        if check_version == 0:
            name = input("Enter Device ID  : ")
        else:
            name = raw_input("Enter Device ID  : ")

        while len(name) != 12:
            print("Must be of length 12")
            if check_version == 0:
                name = input("Enter Device ID  : ")
            else:
                name = raw_input("Enter Device ID  : ")

        if check_version == 0:
            userpass = input("Enter Password : ")
        else:
            userpass = raw_input("Enter Password : ")

        while checker(userpass, length=64):
            if check_version == 0:
                userpass = input("Enter Password : ")
            else:
                userpass = raw_input("Enter Password : ")

        if check_version == 0:
            wifi = input("Enter WiFi (Router's name)  : ")
        else:
            wifi = raw_input("Enter WiFi (Router's name)  : ")

        while checker(wifi, length=32):
            if check_version == 0:
                wifi = input("Enter WiFi (Router's name)  : ")
            else:
                wifi = raw_input("Enter WiFi (Router's name)  : ")

        # *************************************************************************************************
        credits = [name, userpass, wifi]
        path3 = dirname + "/data/temp"
        os.chmod(path3, 0o600)
        with open(path3, 'w') as f:
            json.dump(credits, f)
        # *************************************************************************************************

        if check_version == 0:
            password = input("Enter WiFi passowrd  : ")
        else:
            password = raw_input("Enter WiFi passowrd  : ")

        while checker(password, length=64):
            if check_version == 0:
                password = input("Enter WiFi passowrd  : ")
            else:
                password = raw_input("Enter WiFi passowrd  : ")

        if check_version == 0:
            check = input("Should sub network information need to be collected yes or no  : ")
        else:
            check = raw_input("Should sub network information need to be collected yes or no  : ")

        if check_version == 0:
            daily_scan = input("Do you want to run daily sub-computer scan on this computer ( ! Helps to update the computer list)  yes/no: ")
        else:
            daily_scan = raw_input("Do you want to run daily sub-computer scan on this computer ( ! Helps to update the computer list)  yes/no: ")

        print("????????????????????????????????????????????????????????????????????????")
        if check_version == 0:
            submit = input("Do you finally wants to submit all above info? Sure!  yes/no: ")
        else:
            submit = raw_input("Do you finally wants to submit all above info? Sure!  yes/no: ")

        if submit != 'yes':
            return 0

        # ********************************************** daily.py to cron *********************************
        if daily_scan == 'yes':
            cron = CronTab(user='root')
            cmd_run = dirname + '/daily.py &'
            cmd_run = "python3 " + cmd_run
            job2 = cron.new(command=cmd_run, comment='daily_run')
            job2.minute.every(2)  # change it to hourly 888888880000000000000000000
            cron.write()

            for jobs in cron:
                print(jobs)

        # ************************************************************************************
        all_jsons['wifi'] = [wifi, password]
        all_jsons['host_computer'] = [host_name, host_mac]

        if check == 'yes':
            all_jsons['sub_host'] = jsondata
        else:
            all_jsons['sub_host'] = []

        collect_json_data = json.dumps(all_jsons)

        # print(collect_json_data)

        send = "http://"
        send += name
        send += ":"
        send += userpass
        send += "@"
        # send += "127.0.0.1:8000/api/data"
        send += "18.202.17.224:5003/api/data"

        try:
            r = requests.post(send, data=collect_json_data)
            if r.status_code == 200:
                print("Process completed successfully")
                return 1
            else:
                print("Please check internet connection or Enter correct Device ID and password")
                return 0

        except:
            print("FAILED to connect to server, Please check internet connection ")
            return 0
        # r = requests.post('http://username:userpass@127.0.0.1:8000/api/data', data=json.dumps(data))

        # ************************************************************************************

    except:
        print("error")


def format_data():
    global host_name
    global host_mac
    global check_version
    global dirname
    global names
    global macs

    print("Formating the output")

    try:
        path = dirname + "/data/data.txt"
        path2 = dirname + "/data/output.txt"
        f = open(path, "w")
        p = subprocess.check_output(["sudo", "awk", "/server/ {print $2}", path2]).decode("utf-8")
        f.write(p)
        f.close()

        path = dirname + "/data/data2.txt"
        f = open(path, "w")
        p = subprocess.check_output(["sudo", "awk", "/server/ {print $NF}", path2]).decode("utf-8")
        f.write(p)
        f.close()

        # sudo awk '/192/ {print $1,$2}' "output2.txt"
        path = dirname + "/data/data3.txt"
        path2 = dirname + "/data/output2.txt"
        f = open(path, "w")
        p = subprocess.check_output(["sudo", "awk", "/192/ {print $1}", path2]).decode("utf-8")
        f.write(p)
        f.close()

        path = dirname + "/data/data4.txt"
        f = open(path, "w")
        p = subprocess.check_output(["sudo", "awk", "/192/ {print $2}", path2]).decode("utf-8")
        f.write(p)
        f.close()

        # **************************************************************************************************
        with open(dirname + '/data/data.txt') as f:
            names = f.readlines()
        f.close()
        names = [x.strip() for x in names]

        with open(dirname + '/data/data2.txt') as f:
            macs = f.readlines()
        f.close()
        macs = [x.strip() for x in macs]

        with open(dirname + '/data/data3.txt') as f:
            names2 = f.readlines()
        f.close()
        names2 = [x.strip() for x in names2]

        with open(dirname + '/data/data4.txt') as f:
            macs2 = f.readlines()
        f.close()
        macs2 = [x.strip() for x in macs2]

        mac_tracker = []
        for m in macs2:
            n = macs2.index(m)
            for x in macs:
                if (m != x) and (n not in mac_tracker):
                    mac_tracker.append(n)

        print(len(mac_tracker))
        # print(mac_tracker)

        for x in mac_tracker:
            macs.append(macs2[x])
            names.append(names2[x])

        path1 = dirname + "/data/main_names.json"
        path2 = dirname + "/data/main_macs.json"

        with open(path1, 'w') as f:
            json.dump(names, f)

        with open(path2, 'w') as f:
            json.dump(macs, f)


    except:
        print("error in formatting")


def finder():
    if not os.geteuid() == 0:
        sys.exit("\nOnly root can run this script (Run with sudo on ubuntu)\n")

    comp_info()
    ethtool_x_cp()
    cron_jobs()
    soft_install()
    tool_run()
    format_data()

    while (send_data() != 1):
        print("")
        print("<<<<<<<<<Please try again, ( or Enter <ctrl+Z) to exit>>>>>>>>>>>>>>")
        print("")


def main():
    finder()
    # test()


if __name__ == '__main__':
    finder()
