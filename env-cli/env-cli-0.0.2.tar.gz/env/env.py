#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def GetHome():
    return os.environ['HOME']

def GetEnvHome():
    home = GetHome()

    env_home = os.path.join(home, '.env')

    if not os.path.exists(env_home):
        os.mkdir(env_home)

    return env_home

def Build():
    '''
    this is build demo
    '''
    try:
        import sys

        scons_path = os.path.join(sys.prefix, 'lib', 'scons')
        # print(scons_path)
        sys.path = sys.path + [scons_path, os.path.dirname(__file__)]

        import SCons.Script

        SCons.Script.main()
    except Exception as e:
       print('building with scons failed!')
       print(e)

    return

def Config():
    print('to config!')
    return

def Env():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'config':
            Config()
            exit(1)

    Build()

if __name__ == '__main__':
    Build()
