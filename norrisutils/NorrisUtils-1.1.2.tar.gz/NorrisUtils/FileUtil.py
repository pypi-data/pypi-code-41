import os
import shutil
import hashlib
import stat


# 查找文件夹中的某个文件
def findMyFileDir(dirPath, findFile):
    files = []
    dirs = []
    for root, dirs, files in os.walk(dirPath, topdown=False):
        for file in files:
            if file == findFile:
                return root
        for dir in dirs:
            findMyFileDir(os.path.join(root, dir), findFile)


# 创建一个文件夹
def createDir(dirPath):
    os.makedirs(dirPath, exist_ok=True)


# 删除一个文件
def delFile(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)


# 删除文件夹里所有的文件
def delDir(dir):
    if (os.path.isdir(dir)):
        for f in os.listdir(dir):
            delDir(os.path.join(dir, f))
        if (os.path.exists(dir)):
            os.rmdir(dir)
    else:
        if (os.path.exists(dir)):
            os.remove(dir)


# 拷贝文件
def copyFile(sourceFilePath, destFilePath):
    if not (os.path.exists(sourceFilePath)):
        return False

    if os.path.exists(destFilePath):
        if getFileMd5(sourceFilePath) == getFileMd5(destFilePath):
            return True
        else:
            os.remove(destFilePath)

    destFileDir = os.path.dirname(destFilePath)
    os.makedirs(destFileDir, exist_ok=True)
    if not (shutil.copyfile(sourceFilePath, destFilePath, follow_symlinks=False)):
        return False
    return True


# 拷贝文件夹里的文件
def copyDir(sourceDir, destDir):
    if not (os.path.exists(sourceDir)):
        return False

    if os.path.exists(destDir):
        shutil.rmtree(destDir)

    if not (shutil.copytree(sourceDir, destDir, symlinks=True)):
        return False
    return True


# 获取文件的md5
def getFileMd5(filePath):
    with open(filePath, 'rb') as f:
        content = f.read()
    hash = hashlib.md5()
    hash.update(content)
    return hash.hexdigest()


# 获取一个文件夹里的所有的文件和该文件对应的md5
def dirList(dirPath):
    listDict = {}
    files = []
    dirs = []
    for root, dirs, files in os.walk(dirPath, topdown=False, followlinks=True):
        for file in files:
            filePath = os.path.join(root, file)
            listDict[os.path.relpath(filePath, dirPath).replace(
                '\\', '/')] = getFileMd5(filePath)
    for dir in dirs:
        dirList(os.path.join(root, dir))
    return listDict


# 逐行读一个文件，并过来文件中某些行里回车和空格
def readLineForFile(filePath):
    f = open(filePath, 'r')
    lines = f.readlines()
    f.close()
    newLines = []
    for line in lines:
        line = line.replace('\n', '').strip()
        if line:
            newLines.append(line)
    return newLines


# 保存
def saveDict(dict, fileName='temp.cache'):
    file = open(fileName, 'w')
    file.write(str(dict))
    file.close()


# 读取
def loadDict(fileName='temp.cache'):
    dict = {}
    try:
        file = open(fileName, 'r')
        binary = file.read()
        dict = eval(binary)
        file.close()
    except:
        pass
    return dict
