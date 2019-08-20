from zlsrc.zljianzhu import jianzhu_gg
from zlsrc.zljianzhu import jianzhu_gg2
from zlsrc.zljianzhu import jianzhu_gg3
from zlsrc.zljianzhu import jianzhu_gg4


##增量更新只需更新一个筛选条件
def work(conp,**args):
    jianzhu_gg.work(conp,**args)


##全量爬取
def work_all(conp,**args):
    jianzhu_gg.work(conp, **args)
    jianzhu_gg2.work(conp,**args)
    jianzhu_gg3.work(conp,**args)
    jianzhu_gg4.work(conp,**args)