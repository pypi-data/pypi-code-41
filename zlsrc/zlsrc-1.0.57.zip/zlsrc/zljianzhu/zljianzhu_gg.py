from zlsrc.zljianzhu import jianzhu_gg
from zlsrc.zljianzhu import jianzhu_gg2
from zlsrc.zljianzhu import jianzhu_gg3
from zlsrc.zljianzhu import jianzhu_gg4
import copy

##增量更新只需更新一个筛选条件
def work(conp,**args):
    jianzhu_gg.work(conp,**args)


##全量爬取
def work_all(conp,**args):
    conp1 = copy.deepcopy(conp)
    conp2 = copy.deepcopy(conp)
    conp3 = copy.deepcopy(conp)

    jianzhu_gg.work(conp, **args)
    jianzhu_gg2.work(conp1,**args)
    jianzhu_gg3.work(conp2,**args)
    jianzhu_gg4.work(conp3,**args)