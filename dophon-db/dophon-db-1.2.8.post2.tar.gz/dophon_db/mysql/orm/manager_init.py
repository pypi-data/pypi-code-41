import re
import time
from threading import Thread

from dophon_logger import *

from dophon_db import properties
from dophon_db.mysql.orm import db_obj
from dophon_db.utils import *

logger = get_logger(eval(properties.log_types))

logger.inject_logger(globals())

manager_map = {}

singleton_dbm = None


class ManagerObject:
    pass


def manager_map_to_object():
    result = ManagerObject()
    for k, v in manager_map.items():
        setattr(result, k, v)
    return result


def init_orm_manager(table_list: list = [], conn_kwargs: dict = {}, orm_pre_load: bool = properties.orm_pre_load):
    global manager_map, singleton_dbm
    manager = db_obj.OrmManager()
    # print(conn_kwargs)
    db_obj.init_pool_in_manager(manager, conn_kwargs)
    if table_list or orm_pre_load:
        db_obj.init_tables_in_db(manager, table_list, conn_kwargs)
    else:
        pass
        # logger.info('对象映射改为运行时映射')
    if conn_kwargs:
        manager_label = conn_kwargs['alias']
        manager_map[manager_label] = manager
        return manager_map_to_object()
    else:
        if singleton_dbm:
            return singleton_dbm
        singleton_dbm = manager
        # logger.info(manager_map)
        return manager


def init_cluster_orm_manager():
    global manager_map
    if manager_map:
        return manager_map
    db_cluster_info = get_db_cluster_info()
    for cluster_info in db_cluster_info:
        for cluster_name in cluster_info:
            logger.info('初始化分片%s数据库 : %s' % (cluster_name, '::'.join(
                [(str(re.sub('_', '', k)) + '<' + str(v) + '>') for
                 k, v in cluster_info[cluster_name].items() if not re.match('.*(user|password).*', k)]
            ),))
            # orm内部管理器初始化方式启动
            # Thread(target=db_obj.init_tables_in_db, args=(manager,),
            #        kwargs={'conn_kwargs': cluster_info[cluster_name]}).start()
            Thread(target=init_orm_manager,
                   kwargs={
                       'table_list': cluster_info[cluster_name]['table_list'],
                       'conn_kwargs': cluster_info[cluster_name]
                   }).start()
    while len(manager_map) != len(db_cluster_info):
        # print(len(manager_map),'---',len(db_cluster_info))
        time.sleep(1)
    return manager_map


class ClusterManager:
    __map = {}

    def __init__(self):
        self.__map = init_cluster_orm_manager()

    def __getattr__(self, name):
        logger.info(f'获取相应对象管理{name}')
        result = None
        # print(self.__map)
        for k, v in self.__map.items():
            # print(k,'---',v)
            if not result:
                if v.has_table(name):
                    result = eval('v.' + name)
                else:
                    try:
                        result = eval('v.' + name)
                    except KeyError as ke:
                        # print(ke)
                        pass
        if result:
            return result
        else:
            raise Exception('无法识别的表名')
