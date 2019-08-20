#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API for the command-line I{xyscript} tool.
"""
# from __future__ import with_statement
import getopt, sys, os, stat

from git import Repo

from xyscript.ios.CommonScript import IOSProjectTool, GitLabTool
from xyscript.ios.cert import Cert
from xyscript.ios.package import Package
from xyscript.common.xylog import *
import xyscript.common.globalvar as gv
from xyscript.config import log_store_local
from xyscript.config import Config
from xyscript.common.sysenv import SysEvn,System
from xyscript.ios.oclint import OCLint

PROJECT_ADDRESS = None      #项目地址
PROJECT_BRANCH = None       #项目分支
TEST_PLATFORM = None        #打包平台
NET_ENV = None              #网络环境
PROJECT_VERSION= None       #项目版本号
PROJECT_BUILD = None        #项目build号
LOG_OR_NOT = None           #是否打印日志到本地
DEV_BRANCH = None           #开发分支
PACKAGE_BRANCH = None       #打包分支
TAG_NAME = None             #tag名
PACKAGE_ORDER = None        #打包顺序
CACHE_PATH = None           #符号表缓存路径
CERT_PASSWORD = None        #证书密码
NOTIFICATION_EMAILS = None  #
WITHOUT_POD_INSTALL = False #不需要$pod install


__all__ = ['pull', 'pullsubmodule', 'initproject', 'package', "pps", 'syn', 'merge','diagnose', 'main']

# #####################################################################################################################################################
# #####################################################################################################################################################
# #####################################################      system method    #########################################################################
# #####################################################################################################################################################
# #####################################################################################################################################################
def _print_helpdoc():
    print("\033[4;30musage:\033[0m")
    print("     \033[0;32mxyscript [action] [parameters(optional)]\033[0m ")
    print("\033[4;30msystem command:\033[0m")
    print("     \033[0;32m[-h]\033[0m or \033[0;32m[--help]\033[0m     \thelpdocument for xyscript")
    print("     \033[0;32m[-v]\033[0m or \033[0;32m[--version]\033[0m   \tversion of xyscript")
    print("\033[4;30mxyscript actions:\033[0m")
    print("     \033[0;32m+ pullsubmodule\033[0m       \tpull submoudle form remote"  )
    print("     \033[0;32m+ pull\033[0m                \tadd change_brach and pull_shellproject to pullsubmodule function"  )
    print("     \033[0;32m+ syn\033[0m                 \tpull latest certs"  )
    print("     \033[0;32m+ pps\033[0m                 \tconfig the certs"  )
    print("     \033[0;32m+ package\033[0m             \tpackage for test")
    print("     \033[0;32m+ merge\033[0m               \tmerge code")
    print("     \033[0;32m+ diagnose\033[0m               \tdiagnose static code")
    print("\033[4;30moptional parameters:\033[0m")
    print("     \033[0;34m[-a]\033[0m or \033[0;34m[--address]\033[0m   \turl of project")
    print("     \033[0;34m[-b]\033[0m or \033[0;34m[--branch]\033[0m    \twhich branch to package,default is Develop")
    print("     \033[0;34m[-p]\033[0m or \033[0;34m[--platform]\033[0m  \twhich platform to package to,default is pgyer")
    print("     \033[0;34m[-e]\033[0m or \033[0;34m[--environment]\033[0m  \tnetwork environment to package to,default is release")
    print("     \033[0;34m[-v]\033[0m or \033[0;34m[--version]\033[0m  \tversion number to package to,the default is the same as the project")
    print("     \033[0;34m[-d]\033[0m or \033[0;34m[--build]\033[0m  \tbuild number to package to,the default is the same as the project")
    print("     \033[0;34m[-m]\033[0m or \033[0;34m[--email]\033[0m  \tthe mailbox that receives the result of the operation,the default is the author's")
    print("     \033[0;34m[-k]\033[0m or \033[0;34m[--package]\033[0m \tthe branch of package needed")
    print("     \033[0;34m[-c]\033[0m or \033[0;34m[--code]  \033[0m  \tthe branch of develop")
    print("     \033[0;34m[-g]\033[0m or \033[0;34m[--log]  \033[0m  \tlog locally or not")
    print("     \033[0;34m[-t]\033[0m or \033[0;34m[--tag]  \033[0m  \tname of tag")
    print("     \033[0;34m[-o]\033[0m or \033[0;34m[--order]\033[0m  \torder of package,the default is zero, which means testflight first and pgyer later, and one is pgyer first and testflight later")
    print("     \033[0;34m[-w]\033[0m or \033[0;34m[--password]\033[0m  \tpassword for certs")
    print("     \033[0;34m[--no-pod]\033[0m  \tdo without pod install")

# TODO(m18221031340@163.com):检查是否安装fastlane
def _check_fastlane():
    print("检查是否安装fastlane，如果没有则立即安装fastlane和pgyer插件")
    if Cert().fastlane_is_in_gem() and Cert().fastlane_is_in_brew():
        return True
    return False

# TODO(m18221031340@163.com):检查是否安装cocoapods
def _check_cocoapods():
    print("检查是否安装cocoapods，如果没有则立即安装cocoapods")

def _folder_is_exist(path):
    if os.path.exists(path):
        print("floder is exist")
    else:
        os.mkdir(path)


# #####################################################################################################################################################
# #####################################################################################################################################################
# #####################################################        api method     #########################################################################
# #####################################################################################################################################################
# #####################################################################################################################################################

def initproject(*parameters):
    """
    从零开始初始化项目
    """
    global PROJECT_ADDRESS, PROJECT_BRANCH, TEST_PLATFORM, NET_ENV
    Package().init_project(project_address=PROJECT_ADDRESS, branch_name=PROJECT_BRANCH, platform=TEST_PLATFORM,net_env=NET_ENV)

def package(*parameters):
    """
    自动打包
    """
    global PROJECT_ADDRESS, PROJECT_BRANCH, TEST_PLATFORM, NET_ENV, PROJECT_VERSION, PROJECT_BUILD, NOTIFICATION_EMAILS, TAG_NAME, PACKAGE_ORDER, CACHE_PATH
    #全局变量初始化
    # gv.__init__()
    # gv.set_value("PROJECT_ADDRESS",PROJECT_ADDRESS)
    # gv.set_value("PROJECT_BRANCH",PROJECT_BRANCH)
    # gv.set_value("TEST_PLATFORM",TEST_PLATFORM)
    # gv.set_value("NET_ENV",NET_ENV)
    # gv.set_value("PROJECT_VERSION",PROJECT_VERSION)
    # gv.set_value("PROJECT_BUILD",PROJECT_BUILD)
    # gv.set_value("NOTIFICATION_EMAILS",NOTIFICATION_EMAILS)
    # gv.set_value("TAG_NAME",TAG_NAME)
    # gv.set_value("PACKAGE_ORDER",PACKAGE_ORDER)
    # gv.set_value("CACHE_PATH",CACHE_PATH)
    # gv.set_value("WITHOUT_POD_INSTALL",WITHOUT_POD_INSTALL)

    Package().auto_package(project_address=PROJECT_ADDRESS, branch_name=PROJECT_BRANCH, platform=TEST_PLATFORM,net_env=NET_ENV, project_version=PROJECT_VERSION,project_build=PROJECT_BUILD,tag_name=TAG_NAME,package_order=PACKAGE_ORDER)

def merge(*parameters):
    """
    合并代码
    """
    global DEV_BRANCH, PACKAGE_BRANCH, NOTIFICATION_EMAILS
    Package().merge_code(code_branch=DEV_BRANCH, package_branch=PACKAGE_BRANCH,email=NOTIFICATION_EMAILS)

def pull(*parameters):
    """
    切换分支+拉取子模块代码+pull+pod install
    """
    global PROJECT_BRANCH
    #切换分支
    if PROJECT_BRANCH != None:
        Package().change_branch(PROJECT_BRANCH)

    #拉壳工程
    try:
        print("start pull shell")
        repo = Repo(os.getcwd())
        repo.remote().pull()
        successlog("pull shell success")
    except BaseException as error:
        faillog("pull shell failed:" + format(error))
    #拉子模块
    pullsubmodule(parameters)

def pullsubmodule(*parameters):
    """
    切换分支+拉取子模块代码+pod install
    """
    global WITHOUT_POD_INSTALL
    Package().pull_submodule()
    if IOSProjectTool().have_podfile():
        if not WITHOUT_POD_INSTALL:
            IOSProjectTool().run_pod_install()
    else:
        warninglog("No `Podfile' found in the project directory,or maybe it's an android project")    
    
def pps(*parameters):
    """
    配置证书
    """
    global CERT_PASSWORD
    if CERT_PASSWORD is not None:
        SysEvn().set_system_environment("MATCH_PASSWORD",CERT_PASSWORD)
    Cert().run_cert_pps()

def syn(*parameters):
    """
    拉取证书
    """
    global CERT_PASSWORD
    if CERT_PASSWORD is not None:
        SysEvn().set_system_environment("MATCH_PASSWORD",CERT_PASSWORD)
    Cert().run_cert_syn()   

def diagnose(*parameters):
    """
    诊断
    """
    global PROJECT_BRANCH,PROJECT_ADDRESS,DEV_BRANCH,PROJECT_BUILD,TAG_NAME,PACKAGE_ORDER

    git_objc = {}
    git_objc['project_url'] = TAG_NAME 	
    git_objc['branch_name'] = PROJECT_BRANCH 
    git_objc['commit_content'] = PACKAGE_ORDER 
    git_objc['commit_url'] = PROJECT_ADDRESS
    git_objc['commit_id'] = PROJECT_BUILD
    git_objc['cc'] = DEV_BRANCH
    if PROJECT_BRANCH == None or PROJECT_ADDRESS == None or DEV_BRANCH == None or PROJECT_BUILD == None or TAG_NAME == None or PACKAGE_ORDER == None:
        git_objc = None

    OCLint().run_oclint(git_objc)

# #####################################################################################################################################################
# #####################################################################################################################################################
# #####################################################       main method     #########################################################################
# #####################################################################################################################################################
# #####################################################################################################################################################

def run_method(args=None):
    global LOG_OR_NOT
    try:
        if LOG_OR_NOT == True and LOG_OR_NOT is not None:
            sys.stdout = Log()
        parameters = args[1:]
        eval(args[0])(parameters)
    except BaseException as error:
        faillog(error)
        _print_helpdoc()
    else:
        Config().check_version()
        if LOG_OR_NOT and LOG_OR_NOT is not None:
            os.system("exit")
        # print("调用方法：", args[0], "成功")

def sys_action(args):
    for parms in args:
        if parms in ("-h", "--help"):
            _print_helpdoc()
            Config().check_version()
            sys.exit()
        elif parms in ("-v", "--version"):
            print(Config().get_version())
            Config().check_version()
            sys.exit() 

class Usage(Exception):
    def __init__(self,msg):
        self.msg = msg

def main(prog=None,args=None):
    global PROJECT_ADDRESS, PROJECT_BRANCH, TEST_PLATFORM, NET_ENV, PROJECT_VERSION, PROJECT_BUILD, NOTIFICATION_EMAILS, PACKAGE_BRANCH, DEV_BRANCH, LOG_OR_NOT,TAG_NAME,PACKAGE_ORDER, CACHE_PATH, CERT_PASSWORD, WITHOUT_POD_INSTALL
    #处理系统方法
    sys_action(sys.argv)  

    args = sys.argv[2:]
    shortargs = 'a:p:b:e:n:d:m:gk:c:t:o:w:' #短选项模式
    longargs = ['address=', 'platform=', 'branch=', 'environment=', 'version=', 'build=', 'email=', 'log', 'package=','code=','tag=','order=','cache=','password=','no-pod'] #长选项模式
    try:
        try:
            opts, args = getopt.getopt(args, shortargs, longargs)
        except getopt.GetoptError as error:
            # 调用具体方法,手动异常
            raise Usage(error.msg)
        else:
            # print('args:',args)
            # print('opts:',opts)
            for opt, arg in opts:
                if opt in ("-a", "--address"):
                    PROJECT_ADDRESS = arg
                elif opt in ("-b", "--branch"):
                    PROJECT_BRANCH = arg
                elif opt in ("-p", "--platform"):
                    TEST_PLATFORM = arg
                elif opt in ("-e", "--environment"):
                    NET_ENV = arg
                elif opt in ("-n", "--version"):
                    PROJECT_VERSION = arg
                elif opt in ("-d", "--build"):
                    PROJECT_BUILD = arg
                elif opt in ("-m", "--email"):
                    NOTIFICATION_EMAILS = arg
                elif opt in ("-k", "--package"):
                    PACKAGE_BRANCH = arg
                elif opt in ("-c", "--code"):
                    DEV_BRANCH = arg
                elif opt in ("-g", "--log"):
                    LOG_OR_NOT = True
                elif opt in ("-t", "--tag"):
                    TAG_NAME = arg
                elif opt in ("-o", "--order"):
                    PACKAGE_ORDER = arg
                elif opt in ("--cache"):
                    CACHE_PATH = arg
                elif opt in ("-w", "--password"):
                    CERT_PASSWORD = arg
                elif opt in ("--no-pod"):
                    WITHOUT_POD_INSTALL = True
                
            run_method(sys.argv[1:])
    except Usage:
        # print("参数解析异常")
        _print_helpdoc()
    

if __name__ == "__main__":
    pass
    _print_helpdoc()

