import subprocess
from subprocess import Popen
import dotenv 
import requests_unixsocket
import os
from ain.instanceUtil import InstanceUtil 
import ain.constants as constants

class Worker():

  def __init__(self):
    self.ENVS = dotenv.dotenv_values(constants.ENV_FILE_PATH)
    self.session = requests_unixsocket.Session()
    self.hostTtydSocket = f'{constants.SHARED_PATH}/ain_worker_ttyd.sock'
    sharedPath = constants.SHARED_PATH.replace("/", '%2F')
    self.workerAddress =  f'http+unix://{sharedPath}%2Fain_worker.sock'
    
  def start(self, optionRun):
    
    for key in optionRun:
      if self.ENVS[key].replace(" ", "") == "" and optionRun[key] == "":
        print(f'[-] {key} empty')
        return

      if optionRun[key] != "":
        dotenv.set_key(constants.ENV_FILE_PATH, key, optionRun[key])

    print("[?] Do you want to start? (y/n)")
    answer = input()
    if (answer.lower() != 'y'):
      return

    
    
    # open provider's ttys socket 
    InstanceUtil.createTtyd(self.hostTtydSocket)

    # open docker container for ain worker server
    InstanceUtil.createContainer(constants.IMAGE, optionRun["GPU"])


  def status(self):
    try:
      response = self.session.get(self.workerAddress + "/info")
      ids = response.json()['id']
      if(len(ids) == 0):
        print("[+] does not exist")
        return
    except Exception as e:
      print("[-] worker server error")
      print(e)
      exit(1)

    print("[+] Status: Running")
    try:
      option = " ".join(ids)
      subprocess.run(["docker", "stats" , option])

    except Exception as e:
      print("[-] subprocess(docker) error")
      print(e)

  def stop(self):
    try:      
      response = self.session.get(self.workerAddress + "/info")
      cnt = response.json()['cnt']
      if (cnt != 0):
        print("[+] instance count:" +str(cnt))
      print("[?] (y/n)")
      answer = input()
      if (answer.lower() != 'y'):
        return
    except Exception as e:
      print("[-] worker server error - info")

    try:
      response = self.session.get(self.workerAddress + "/terminate")
    except Exception as e:
      print("[-] worker server error - terminate")

    try:
      InstanceUtil.removeContainer("ain_worker")
      print('[+] succeded to remove container!')

    except Exception as e:
      print("[-] subprocess(docker) error")
      print(e)

    try:
      InstanceUtil.removeTtyd(self.hostTtydSocket)
      InstanceUtil.removeTtyd(f'{constants.SHARED_PATH}/ain_worker.sock')
      print('[+] succeded to remove ttyd socket')
    except Exception as e:
      print("[-] subprocess error(ttyd socker remove)")
      print(e)
      exit(1)

  def log(self):
    basePath = constants.SHARED_PATH + "/log/" 
    if (os.path.exists(basePath + "log.env")):
      os.remove(basePath + "log.env")
    logFileName = os.listdir(basePath)
    times = [i.split("_")[2].split(".")[0] for i in logFileName]
    if (len(times) == 0):
      print("[+] does not exist")
      return
  
    print("[?] do you want to see recent log?(y/n)")
    answer = input()
    if (answer == "n"):
      for i in range(len(logFileName)):
        print(str(i) + " - " + logFileName[i])
      print("[?] input number")
      try:
        number = int(input())
        path = os.path.join(basePath, logFileName[number])
        subprocess.run(["cat", path])
      except Exception as e:
        print("[-] subprocess(log) error")
        print(e)
        return
    times.sort()             
    try:
      path = os.path.join(basePath, "ain_worker_" + times[-1] + ".log")
      subprocess.run(["tail", "-f" , path])
    except Exception as e:
      print("[-] subprocess(log) error")
      print(e)

  def init(self):
    for key in ["NAME", "LIMIT_COUNT", "PRICE", "DESCRIPTION", "MNEMONIC", "SERVER_IP", "GPU"]:
      dotenv.set_key(constants.ENV_FILE_PATH, key, "")
      
  def version(self):
    try:
      response = self.session.get(self.workerAddress + "/version")
      print(response.json()['version'])
    except Exception as e:
      print("[-] worker server error")
      print(e)
      exit(1)
