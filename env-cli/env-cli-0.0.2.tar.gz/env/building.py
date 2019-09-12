#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# File      : building.py
# This file is part of RT-Thread RTOS
# COPYRIGHT (C) 2006 - 2019, RT-Thread Development Team
#
# Change Logs:
# Date           Author       Notes
# 2019-05-26     Bernard      The first version
#

import os
import sys
import string

from SCons.Script import *

BuildOptions = {}
Projects = []
Env = None
ArchConfig = None

Rtt_Root = ''
BSP_Root = ''
USR_ROOT = ''

def GetCurrentDir():
    conscript = File('SConscript')
    fn = conscript.rfile()
    name = fn.name
    path = os.path.dirname(fn.abspath)
    return path

def GetDepend(depend):
    # always true
    return True

def MergeGroup(src_group, group):
    src_group['src'] = src_group['src'] + group['src']

    def dict_append(d1, d2, key):
        if key in d2:
            if key in d1:
                d1[key] = d1[key] + d2[key]
            else:
                d1[key] = d2[key]

    dict_append(src_group, group, 'CCFLAGS')
    dict_append(src_group, group, 'CPPPATH')
    dict_append(src_group, group, 'CPPDEFINES')

    dict_append(src_group, group, 'LOCAL_CCFLAGS')
    dict_append(src_group, group, 'LOCAL_CPPPATH')
    dict_append(src_group, group, 'LOCAL_CPPDEFINES')

    dict_append(src_group, group, 'LINKFLAGS')
    dict_append(src_group, group, 'LIBS')
    dict_append(src_group, group, 'LIBPATH')

def DefineGroup(name, src, depend, **parameters):
    global Env
    if not GetDepend(depend):
        return []

    # find exist group and get path of group
    group_path = ''
    for g in Projects:
        if g['name'] == name:
            group_path = g['path']
    if group_path == '':
        group_path = GetCurrentDir()

    group = parameters
    group['name'] = name
    group['path'] = group_path
    if type(src) == type(['src1']):
        group['src'] = File(src)
    else:
        group['src'] = src

    if 'CCFLAGS' in group:
        Env.Append(CCFLAGS = group['CCFLAGS'])
    if 'CPPPATH' in group:
        Env.Append(CPPPATH = group['CPPPATH'])
    if 'CPPDEFINES' in group:
        Env.Append(CPPDEFINES = group['CPPDEFINES'])
    if 'LINKFLAGS' in group:
        Env.Append(LINKFLAGS = group['LINKFLAGS'])

    if 'LIBS' in group:
        Env.Append(LIBS = group['LIBS'])
    if 'LIBPATH' in group:
        Env.Append(LIBPATH = group['LIBPATH'])

    if 'LIBRARY' in group:
        objs = Env.Library(name, group['src'])
    else:
        objs = group['src']

    # merge group
    for g in Projects:
        if g['name'] == name:
            # merge to this group
            MergeGroup(g, group)
            return objs

    # add a new group
    Projects.append(group)

    return objs

def BuildConfiguration(Toolchain = None, CPU_Arch = None):
    global ArchConfig
    EXEC_PATH = None

    # try read configuration files
    if USR_ROOT and Toolchain == None and CPU_Arch == None:
        from config import ParseConfig

        config = ParseConfig(os.path.join(USR_ROOT, '.config'))

        CPU_Arch = config['ARCH']
        Toolchain = config['Toolchain']
        EXEC_PATH = config['EXEC_PATH']

    # get EXEC_PATH from environment
    if os.getenv('EXEC_PATH'):
        EXEC_PATH = os.getenv('EXEC_PATH')

    # Build Configuration for Toolchain, CPU/Arch
    if CPU_Arch == 'Cortex-M0':
        from cortexm import ARCHCortexM
        ArchConfig = ARCHCortexM(Toolchain = Toolchain, CPU_Arch = CPU_Arch, EXEC_PATH = EXEC_PATH)
    elif CPU_Arch == 'Cortex-M3':
        from cortexm import ARCHCortexM
        ArchConfig = ARCHCortexM(Toolchain = Toolchain, CPU_Arch = CPU_Arch, EXEC_PATH = EXEC_PATH)
    elif CPU_Arch == 'Cortex-M4':
        from cortexm import ARCHCortexM
        ArchConfig = ARCHCortexM(Toolchain = Toolchain, CPU_Arch = CPU_Arch, EXEC_PATH = EXEC_PATH)
    elif CPU_Arch == 'Cortex-M7':
        from cortexm import ARCHCortexM
        ArchConfig = ARCHCortexM(Toolchain = Toolchain, CPU_Arch = CPU_Arch, EXEC_PATH = EXEC_PATH)
    elif CPU_Arch == 'Cortex-M23':
        from cortexm import ARCHCortexM
        ArchConfig = ARCHCortexM(Toolchain = Toolchain, CPU_Arch = CPU_Arch, EXEC_PATH = EXEC_PATH)
    elif CPU_Arch == 'Cortex-M33':
        from cortexm import ARCHCortexM
        ArchConfig = ARCHCortexM(Toolchain = Toolchain, CPU_Arch = CPU_Arch, EXEC_PATH = EXEC_PATH)
    elif CPU_Arch == 'Cortex-A':
        from cortexa import ARCHCortexA
        ArchConfig = ARCHCortexA(Toolchain = Toolchain, CPU_Arch = CPU_Arch, EXEC_PATH = EXEC_PATH, USR_ROOT = USR_ROOT)


    from gcc import GenerateGCCConfig
    GenerateGCCConfig(ArchConfig)

    return

# create the environment
def BuildEnv():
    global Env

    # get toolchain configuration
    BuildConfiguration()

    env = Environment(tools = ['mingw'],
        AS   = ArchConfig.AS, ASFLAGS = ArchConfig.AFLAGS,
        CC   = ArchConfig.CC, CCFLAGS = ArchConfig.CFLAGS,
        CXX  = ArchConfig.CXX, CXXFLAGS = ArchConfig.CXXFLAGS,
        AR   = ArchConfig.AR, ARFLAGS = '-rc',
        LINK = ArchConfig.LINK, LINKFLAGS = ArchConfig.LFLAGS)
    env.PrependENVPath('PATH', ArchConfig.EXEC_PATH)
    env['ASCOM'] = env['ASPPCOM']
    Env = env

    if not GetOption('verbose'):
        # override the default verbose command string
        env.Replace(
            ARCOMSTR = 'AR $TARGET',
            ASCOMSTR = 'AS $TARGET',
            ASPPCOMSTR = 'AS $TARGET',
            CCCOMSTR = 'CC $TARGET',
            CXXCOMSTR = 'CXX $TARGET',
            LINKCOMSTR = 'LINK $TARGET'
        )

    return env

def BuildRTThread(TARGET, env = None):
    global BuildOptions

    # parse rtconfig.h to build BuildOptions
    PreProcessor = PatchedPreProcessor()

    contents = ''
    try:
        contents = open('rtconfig.h', 'r').read()
    except e:
        print('No rtconfig.h found.')
        exit(-1)
    PreProcessor.process_contents(contents)
    BuildOptions = PreProcessor.cpp_namespace

    return

def BuildHostApplication(TARGET, SConscriptFile):
    import platform
    global Env

    platform_type = platform.system()
    if platform_type == 'Windows' or platform_type.find('MINGW') != -1:
        TARGET = TARGET.replace('.mo', '.exe')

    HostRtt = os.path.join(os.path.dirname(__file__), 'host', 'rtthread')
    Env = Environment()

    if not GetOption('verbose'):
        # override the default verbose command string
        Env.Replace(
            ARCOMSTR = 'AR $TARGET',
            ASCOMSTR = 'AS $TARGET',
            ASPPCOMSTR = 'AS $TARGET',
            CCCOMSTR = 'CC $TARGET',
            CXXCOMSTR = 'CXX $TARGET',
            LINKCOMSTR = 'LINK $TARGET'
        )

    objs = SConscript(SConscriptFile)
    objs += SConscript(HostRtt + '/SConscript')

    target = Env.Program(TARGET, objs)
    return

def BuildApplication(TARGET, SConscriptFile, usr_root = None):
    global USR_ROOT

    # add comstr option
    AddOption('--verbose',
                dest='verbose',
                action='store_true',
                default=False,
                help='print verbose information during build')

    # build application in host 
    if usr_root == None:
        BuildHostApplication(TARGET, SConscriptFile)
        return

    USR_ROOT = os.path.abspath(usr_root)
    env = BuildEnv()

    target_vdir = 'build'
    objs = SConscript(SConscriptFile, variant_dir=target_vdir, duplicate=0)
    # include crt/libraries
    objs.extend(SConscript(USR_ROOT + '/sdk/crt/SConscript', variant_dir=target_vdir + '/crt', duplicate=0))

    # build program
    if TARGET.find('.') == -1:
        TARGET = TARGET + '.' + ArchConfig.TARGET_EXT
    target = Env.Program(TARGET, objs)

def BuildHostLibrary(TARGET, SConscriptFile):
    import platform
    global Env

    platform_type = platform.system()
    if platform_type == 'Windows' or platform_type.find('MINGW') != -1:
        TARGET = TARGET.replace('.mo', '.exe')

    HostRtt = os.path.join(os.getcwd(), 'tools', 'host', 'rtthread')
    Env = Environment()

    if not GetOption('verbose'):
        # override the default verbose command string
        Env.Replace(
            ARCOMSTR = 'AR $TARGET',
            ASCOMSTR = 'AS $TARGET',
            ASPPCOMSTR = 'AS $TARGET',
            CCCOMSTR = 'CC $TARGET',
            CXXCOMSTR = 'CXX $TARGET',
            LINKCOMSTR = 'LINK $TARGET'
        )

    objs = SConscript(SConscriptFile)
    objs += SConscript(HostRtt + '/SConscript')

    target = Env.Program(TARGET, objs)
    return

def BuildLibrary(TARGET, SConscriptFile, BSP_ROOT = None, RTT_ROOT = None):
    global Env
    global Rtt_Root
    global BSP_Root

    # add comstr option
    AddOption('--verbose',
                dest='verbose',
                action='store_true',
                default=False,
                help='print verbose information during build')

    # build application in host 
    if BSP_ROOT == None and RTT_ROOT == None and not os.getenv('BSP_ROOT'):
        BuildHostLibrary(TARGET, SConscriptFile)
        return

    if RTT_ROOT == None and os.getenv('RTT_ROOT'):
        RTT_ROOT = os.getenv('RTT_ROOT')

    # handle BSP_ROOT and RTT_ROOT
    SetRoot(BSP_ROOT, RTT_ROOT)

    sys.path = sys.path + [os.path.join(Rtt_Root, 'tools'), BSP_Root]

    # get configuration from BSP 
    import rtconfig 
    from rtua import GetCPPPATH
    from rtua import GetCPPDEFINES

    linkflags = rtconfig.M_LFLAGS + ' -e 0'
    CPPPATH = GetCPPPATH(BSP_Root, Rtt_Root)

    if rtconfig.PLATFORM == 'cl': 
        Env = Environment(TARGET_ARCH='x86')
        Env.Append(CCFLAGS=rtconfig.M_CFLAGS)
        Env.Append(LINKFLAGS=rtconfig.M_LFLAGS)
        Env.Append(CPPPATH=CPPPATH)
        Env.Append(LIBS='rtthread', LIBPATH=BSP_Root)
        Env.Append(CPPDEFINES=GetCPPDEFINES() + ['RTT_IN_MODULE'])
        Env.PrependENVPath('PATH', rtconfig.EXEC_PATH)
    else:
        Env = Environment(tools = ['mingw'],
            AS = rtconfig.AS, ASFLAGS = rtconfig.AFLAGS,
            CC = rtconfig.CC, CCFLAGS = rtconfig.M_CFLAGS,
            CPPDEFINES = GetCPPDEFINES(),
            CXX = rtconfig.CXX, AR = rtconfig.AR, ARFLAGS = '-rc',
            LINK = rtconfig.LINK, LINKFLAGS = linkflags,
            CPPPATH = CPPPATH)

    if not GetOption('verbose'):
        # override the default verbose command string
        Env.Replace(
            ARCOMSTR = 'AR $TARGET',
            ASCOMSTR = 'AS $TARGET',
            ASPPCOMSTR = 'AS $TARGET',
            CCCOMSTR = 'CC $TARGET',
            CXXCOMSTR = 'CXX $TARGET',
            LINKCOMSTR = 'LINK $TARGET'
        )

    objs = SConscript(SConscriptFile)

    # build program 
    if rtconfig.PLATFORM == 'cl':
        dll_target = TARGET.replace('.so', '.dll')
        target = Env.SharedLibrary(dll_target, objs)

        target = Command("$TARGET", dll_target, [Move(TARGET, dll_target)])
        # target = dll_target
    else:
        target = Env.Program(TARGET, objs)

    if hasattr(rtconfig, 'M_POST_ACTION'):
        Env.AddPostAction(target, rtconfig.M_POST_ACTION)
