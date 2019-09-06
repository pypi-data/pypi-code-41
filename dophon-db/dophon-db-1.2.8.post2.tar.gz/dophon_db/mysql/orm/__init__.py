from dophon_logger import *

from dophon_db import properties
from dophon_db.mysql.orm.manager_init import *

logger = get_logger(eval(properties.log_types))

logger.inject_logger(globals())


def init_orm(table_list=[], conn_kwargs={}):
    """
    初始化orm
    :return:
    """
    if getattr(properties, 'db_cluster', []):
        logger.info('分片数据库初始化')
        return ClusterManager()
    else:
        return init_orm_manager(table_list, conn_kwargs)
