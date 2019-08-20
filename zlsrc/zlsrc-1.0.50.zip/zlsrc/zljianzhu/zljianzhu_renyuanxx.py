from zlsrc.zljianzhu import jianzhu_zcry
from zlsrc.zljianzhu import jianzhu_ryxx
import copy

def work(conp,**args):
    conp1=copy.deepcopy(conp)

    jianzhu_zcry.work(conp1,**args)
    jianzhu_ryxx.work(conp1,**args)