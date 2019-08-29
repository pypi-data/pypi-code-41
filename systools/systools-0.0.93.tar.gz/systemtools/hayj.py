
# pew in st-venv python ~/Workspace/Python/Utils/SystemTools/systemtools/hayj.py

from enum import Enum
from systemtools.logger import *
from systemtools.location import *
from systemtools.basics import *
from systemtools.system import *
from datatools.dataencryptor import *
import json
import re

def hjlat():
    return isHostname("hjlat")

def lri():
    if isHostname("tipi") or isHostname("kepler") or isHostname("titanv"):
        return True
    elif isDir(homeDir() + "/NoSave") or isDir("/NoSave"):
        return True
    else:
        return False

def labia():
    return "labia" in getHostname() or "lab-ia" in getHostname()

def tipi():
    return isHostname("tipi") or isHostname("titanv") or isHostname("kepler")

def octods():
    return isHostname("datascience01")

def getCurrentTipiNumber(toInteger=False):
    hostname = getHostname()
    if "tipi" not in hostname:
        return None
    nb = getFirstNumber(hostname)
    if toInteger:
        return nb
    else:
        if nb < 10:
            return "0" + str(nb)
        else:
            return str(nb)

def getAllTipiNumbers(toInteger=False):
    all = []
    for current in range(56, 95):
        all.append(str(current))
    all = listSubstract(all, ["83", "84", "88", "92", "95"])
    for current in range(0, 8):
        all.append("0" + str(current))
    if toInteger:
        for i in range(len(all)):
            all[i] = int(all[i])
    return all

def getAllTipiNumbersButCurrent(*args, **kwargs):
    all = getAllTipiNumbers(*args, **kwargs)
    if getCurrentTipiNumber(*args, **kwargs) is not None:
        current = getCurrentTipiNumber(*args, **kwargs)
        return listSubstract(all, current)
    else:
        return all

def getAllTipiNumbersBut(but, *args, **kwargs):
    if but is None or len(but) == 0:
        return getAllTipiNumbers(*args, **kwargs)
    if "toInteger" not in kwargs:
        if isinstance(but[0], int):
            kwargs["toInteger"] = True
        else:
            kwargs["toInteger"] = False
    if kwargs["toInteger"] and isinstance(but[0], str):
        for i in range(len(but)):
            but[i] = int(but[i])
    if not kwargs["toInteger"] and isinstance(but[0], int):
        for i in range(len(but)):
            but[i] = str(but[i])
    all = getAllTipiNumbers(*args, **kwargs)
    return listSubstract(all, but)

def getSparkMasterSchema(logger=None, verbose=True):
    try:
        if isHostname("tipi") or isHostname("titan"):
            confPath = sortedGlob(homeDir() + "/lib/spark-2.*-bin-hadoop2.7/conf/spark-env.sh")[0]
            if isFile(confPath):
                confText = fileToStr(confPath)
                ip = re.search('\nSPARK_MASTER_HOST=((?:[0-9]{1,3}.){3}[0-9]{1,3})', confText).group(1)
                assert len(ip) > 8
                port = re.search('\nSPARK_MASTER_PORT=([0-9]{2,6})', confText).group(1)
                assert len(port) > 2
                return "spark://" + ip + ":" + port
            else:
                logError(confPath + " not found!", logger, verbose=verbose)
    except Exception as e:
        logException(e, logger, verbose=verbose)
    logWarning("Spark schema not found!", logger, verbose=verbose)
    return None



# MONGO_SERVERS = Enum("MONGO_SERVERS", "localhost datascience01 hjlat jamy tipi")
# def getMongoAuth(user="hayj", mongoServer=MONGO_SERVERS.localhost, passwordsPath=None):
def getMongoAuth(user=None,
                 hostname="localhost",
                 logger=None,
                 verbose=True):
    """
        (user, password, host) = getMongoAuth()
    """
#     def jsonFileToObject(path):
#         with open(path) as data:
#             data = jsonToObject(data)
#         return data
#     def jsonToObject(text):
#         return json.load(text)
    host = "localhost"
#     if mongoServer == "datascience01" and not isHostname("datascience01"):
    if hostname == "datascience01" and not isHostname(hostname):
        host = "212.129.44.40" # 212.129.44.40
    try:
        passwords = getDataEncryptorSingleton(logger=logger, verbose=verbose)["mongoauth"]["datascience01"]
    except Exception as e:
        logException(e, logger, message="Encrypted data in ~/.ssh/encrypted-data not found, a localhost mongodb auth will be used...",
                 verbose=verbose)
        return getLocalhostMongoAuth()

    password = None
    if user is not None:
        password = passwords[user]
    return (user, password, host)

def getOctodsMongoAuth(*args, **kwargs):
    return getDatascience01MongoAuth(*args, **kwargs)
def getDatascience01MongoAuth(*args, **kwargs):
    return getMongoAuth(*args, user="hayj", hostname="datascience01", **kwargs)
def getStudentMongoAuth(*args, **kwargs):
    return getMongoAuth(*args, user="student", hostname="datascience01", **kwargs)
def getAnnotatorMongoAuth(*args, **kwargs):
    return getMongoAuth(*args, user="annotator", hostname="datascience01", **kwargs)
def getHyperoptMongoAuth(*args, **kwargs):
    return getMongoAuth(*args, user="houser", hostname="datascience01", **kwargs)
def getLocalhostMongoAuth(*args, **kwargs):
    if isHostname("datascience01"):
        return getOctodsMongoAuth(*args, **kwargs)
    else:
        return (None, None, "localhost")



# def homeDir(user=None, homePaths=["/users/modhel", "/home"]):
#     if user is None:
#         user = getpass.getuser()
# #         if user in ["root", "admin", "superuser", "mongo", "mongod", "pydev"]:
# #             user = defaultUser
#     for currentHomePath in homePaths:
#         currentPath = currentHomePath + "/" + user
#         if isDir(currentPath):
#             return currentPath
#     return None

# def dataPath(dirname="Data", startDirs=["/users/modhel-nosave/hayj", "/home/hayj"], subDirSamples=["Similarity", "TwitterArchiveOrg"]):
#     walkParams = {"followlinks": True, "topdown": False}
#     pathSamples = []
#     for current in subDirSamples:
#         pathSamples.append(dirname + "/" + current)
#     for startDir in startDirs:
#         for root, dirs, files in os.walk(startDir, topdown=False):
#             for name in dirs:
#                 thePath = os.path.join(root, name)
#                 for sample in pathSamples:
#                     if re.match("^.*" + sample + "$", thePath) is not None:
#                         return "/".join(thePath.split("/")[0:-1])
#     return None

if __name__ == '__main__':
    print(getSparkMasterSchema())
    # print(getHyperoptMongoAuth()[1])
    # printLTS(getAllTipiNumbers(toInteger=True))
