# -*- coding:utf-8 -*-

import cat
import time
import traceback

from kdbase.log import *
from singleton import singleton


base_name = ""

def init(name):
    global base_name
    base_name = name

@singleton
class CatInit(object):
    def __init__(self):
        logger().info('cat init, base name [%s]', base_name)
        cat.init(base_name)

@singleton
class CatStage(object):
    def __init__(self):
        CatInit()
        self.__stage_map = {}

    def stage_begin(self, space, name):
        key = (space, name)
        logger().info('cat begin space[%s], name[%s]', space, name)
        self.__stage_map[key] = cat.Transaction(space, name)

    def stage_end(self, space, name, status):
        key = (space, name)
        assert key in self.__stage_map
        if not status:
            self.__stage_map[key].set_status(cat.CAT_ERROR)
            cat.log_event(space, name, cat.CAT_ERROR)
        else:
            cat.log_event(space, name, cat.CAT_SUCCESS)

        logger().info('cat complete space[%s], name[%s], status[%s]', 
                space, name, status)
        self.__stage_map[key].complete()
        del self.__stage_map[key]

@singleton
class CatStageAgency(object):
    def __init__(self):
        CatInit()
        self.reset()

    def reset(self):
        self.__stage_list = []

    def stage_begin(self, space, name):
        key = (space, name)
        name = '%s/%s' % (space, name)
        tran = cat.Transaction(space, name)
        self.__stage_list.append(tran)

    def finish(self):
        if len(self.__stage_list) > 0:
            logger().info('cat finish, flush %d transactions',
                          len(self.__stage_list))
        for val in self.__stage_list[::-1]:
            val.complete()
        self.__stage_list = []

def cat_wrapper(appkey, space, name):
    def decorator(func):
        def wrapper(*args, **kw):
            try:
                init(appkey)
                stage_begin(space, name)
                f = func(*args, **kw)
                flag = True
                if f == False:
                    flag = False
                stage_end(space, name, flag)
                return f
            except Exception as e:
                stage_end(space, name, False)
                raise
        return wrapper
    return decorator


#----------------Shortcut--------------

def stage_begin(space, name):
    try:
        CatStage().stage_begin(space, name)
    except Exception as e:
        err_msg = traceback.format_exc()
        logger().error('cat error:' + err_msg)

def stage_end(space, name, status=True):
    try:
        CatStage().stage_end(space, name, status)
    except Exception as e:
        err_msg = traceback.format_exc()
        logger().error('cat error:' + err_msg)

def agent_stage_begin(space, name):
    try:
        CatStageAgency().stage_begin(space, name)
    except Exception as e:
        err_msg = traceback.format_exc()
        logger().error('cat error:' + err_msg)

def agent_reset():
    try:
        CatStageAgency().reset()
    except Exception as e:
        err_msg = traceback.format_exc()
        logger().error('cat error:' + err_msg)

def agent_finish():
    try:
        CatStageAgency().finish()
    except Exception as e:
        err_msg = traceback.format_exc()
        logger().error('cat error:' + err_msg)

def log_event(space, name):
    try:
        name = '%s/%s' % (space, name)
        cat.log_event(space, name)
    except Exception as e:
        err_msg = traceback.format_exc()
        logger().error('cat error:' + err_msg)

def test():
    import time
    stage_begin('a', '3')
    stage_begin('a', '4')
    time.sleep(1)
    stage_end('a', '4')
    stage_end('a', '3')

def test2():
    import time
    init('kd.base123')
    agent_stage_begin('b', 'b')
    agent_stage_begin('b', 'c')
    agent_stage_begin('b', 'd')
    time.sleep(1)
    agent_finish()

def test1():
    import time
    cat.init("kd.test")
    a = cat.Transaction('c', 'b')
    time.sleep(2)
    a.complete()
    b = cat.Transaction('c', 'c')
    time.sleep(2)
    b.complete()

def main():
    test2()

if __name__ == '__main__':
    main()




