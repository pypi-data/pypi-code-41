from zlsrc.zljianzhu import jianzhu_gcxm
from zlsrc.zljianzhu import jianzhu_xmxx
import copy

def work(conp,**args):
    conp1=copy.deepcopy(conp)
    jianzhu_gcxm.work(conp1,**args)
    jianzhu_xmxx.work(conp1,**args)
