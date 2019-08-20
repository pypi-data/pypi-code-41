from espapp.esp import comp_info, tool_run, format_data, send_data
from espapp.esp import dirname
import json
import requests


def update_new_comp():
    #    global macs
    #    global names
    #    global dirname

    with open(dirname + '/data/log', 'a') as f:
        f.write("update started")

    path1 = dirname + "/data/main_names.json"
    path2 = dirname + "/data/main_macs.json"

    try:
        with open(path1) as f:
            name2 = json.load(f)

        with open(path2) as f:
            mac2 = json.load(f)

        f.close()

        jsondata = []
        for index in range(0, len(mac2)):
            list = [name2[index], mac2[index]]
            jsondata.append(list)

        #        with open(dirname + '/data/log', 'a') as f:
        #            f.write("dswdwd{0}".format(count))

        #        with open(path1, 'w') as f:
        #            json.dump(names, f)

        #        with open(path2, 'w') as f:
        #            json.dump(macs, f)

        try:
            with open(dirname + '/data/temp') as f:
                array = json.load((f))

            data_update = {}
            data_update["wifi"] = array[2]
            data_update["sub_host"] = jsondata

            collect_json_data = json.dumps(data_update)

        except Exception as ex:
            print(" failed to fetch credit")
            with open(dirname + '/data/log', 'a') as l:
                l.write(type(ex).__name__)

        send = "http://"
        send += array[0]
        send += ":"
        send += array[1]
        send += "@"
        send += "18.202.17.224:5003/api/update_auto"

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



    except Exception as ex:
        print("daily scan fails")
        with open(dirname + '/data/log', 'w') as l:
            l.write(type(ex).__name__)


def daily_runner():
    try:
        comp_info()
        tool_run()
        format_data()  # updates names and macs
        update_new_comp()

    except Exception as ex:
        with open(dirname + '/data/log', 'w') as l:
            l.write(type(ex).__name__)


daily_runner()

