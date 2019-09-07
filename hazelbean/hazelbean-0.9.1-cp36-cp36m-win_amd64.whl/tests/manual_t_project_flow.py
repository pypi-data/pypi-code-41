# NOTE Test is manual because uses CWD directly and inspeciton

import os, sys, time

import hazelbean as hb

# DEVELOPMENT STATE:
# This includes a good idea, having a Path object that is defined as a global in the research script but then is used conditionally based on what is run
# but it isn't finished

L = hb.get_logger('manual_t_project_flow')


# global path1
path1 = hb.Path('data/global_1deg_floats.tif')
af1 = hb.ArrayFrame(path1)

# print(af1)
def calculation_1(p):
    L.debug('Debug 1')
    # L.info('Info 1')
    # L.warning('warning 1')
    # L.critical('critical 1')
    # L.info(af1)
    # L.info(af1.path)
    if p.run_this:
        5


def calculation_2(p):
    L.debug('Debug 2')
    # L.info('Info 2')
    # L.warning('warning 2')
    # L.critical('critical 2')
    if p.run_this:
        print(path1)
        print(p.path1)
        5
        # L.info(af1)


p = hb.ProjectFlow('test_project')
p.add_task(calculation_1)
p.add_task(calculation_2)



p.execute()




