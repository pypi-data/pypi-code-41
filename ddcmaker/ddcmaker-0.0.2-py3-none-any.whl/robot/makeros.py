import json
import subprocess
import time
import os


def linux_maker(data):
    res = {"msg": "", "code": 1, "data": {}}
    # print(data)
    # data = json.loads(request)
    # print(type(data))

    data = str(data, encoding="u8").replace('\r\n', '').replace('    ', '')
    print(data)
    try:
        code = eval(data)["code"]
        print("取出传入的值", code)
    except Exception as e:
        print(e)
        res.update(err="代码不能为空，请输入代码。")
        # print(type(res))
        return json.dumps(res)
    if code == "":
        res.update(err="代码不能为空，请输入代码。")
        # print(type(res))
        return json.dumps(res)

    # fp, file_name = mkstemp(suffix=".py", text=True)
    file_name = str(time.time())[-6:] + ".py"
    print(file_name)
    with open(file_name, "w+", encoding="u8") as f:
        # print(type(code))
        f.write(code)
        f.close()
    # print()
    # cmd = "python3 -IB  "+file_name  # 在linux 下运行为python3

    cmd = "python3 " + file_name
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            # encoding="u8",
                            shell=True)  # 在windows 下运行时为False，linux 下运行为 True

    try:
        out, err = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        res.update(err="机器运行超时，中断机器人链接。")
    else:
        if err:
            res.update(err=err.decode("u8"))
        else:
            res.update(code=0, data={
                "moduleData": [out.decode("u8")],
                "printData": ""
            })
    finally:
        # os.close(fp)
        os.remove(file_name)
    return json.dumps(res)


def windows_maker(data):
    res = {"msg": "", "code": 1, "data": {}}
    # print(data)
    # data = json.loads(request)
    # print(type(data))

    data = str(data, encoding="u8").replace('\r\n', '').replace('    ', '')
    print(data)
    try:
        code = eval(data)["code"]
        print("取出传入的值", code)
    except Exception as e:
        print(e)
        res.update(err="代码不能为空，请输入代码。")
        # print(type(res))
        return json.dumps(res)
    if code == "":
        res.update(err="代码不能为空，请输入代码。")
        # print(type(res))
        return json.dumps(res)

    # fp, file_name = mkstemp(suffix=".py", text=True)
    file_name = str(time.time())[-6:] + ".py"
    print(file_name)
    with open(file_name, "w+", encoding="u8") as f:
        # print(type(code))
        f.write(code)
        f.close()
    # print()
    # cmd = "python3 -IB  "+file_name  # 在linux 下运行为python3
    cmd = "python " + file_name
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            encoding="u8",
                            shell=False)  # 在windows 下运行时为False，linux 下运行为 True

    try:
        out, err = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        res.update(err="机器运行超时，中断机器人链接。")
    else:
        if err:
            res.update(err)
        else:
            res.update(code=0, data={
                "moduleData": [out],
                "printData": ""
            })
    finally:
        # os.close(fp)
        os.remove(file_name)
    return json.dumps(res)


def Mac_maker():
    res = {"msg": "", "code": 1, "data": {}}
    res.update(err="当前系统为Mac,暂时不支持此系统！")
    return json.dumps(res)


def other_maker():
    res = {"msg": "", "code": 1, "data": {}}
    res.update(err="你这是啥系统呀，暂时不支持哟！")
    return json.dumps(res)



