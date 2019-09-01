# coding: UTF-8
from sys import version_info as __1lll1_opy_
l1111_opy_ = __1lll1_opy_[0] == 2
l1ll1l_opy_ = 2048
l11l1_opy_ = 7
def l1l11_opy_ (ll_opy_):
    global l1llll_opy_
    l11lll_opy_ = ord (ll_opy_ [-1])
    l111l_opy_ = ll_opy_ [:-1]
    l1l_opy_ = l11lll_opy_ % len (l111l_opy_)
    l11_opy_ = l111l_opy_ [:l1l_opy_] + l111l_opy_ [l1l_opy_:]
    if l1111_opy_:
        l1ll11_opy_ = unicode () .join ([unichr (ord (char) - l1ll1l_opy_ - (l1ll1_opy_ + l11lll_opy_) % l11l1_opy_) for l1ll1_opy_, char in enumerate (l11_opy_)])
    else:
        l1ll11_opy_ = str () .join ([chr (ord (char) - l1ll1l_opy_ - (l1ll1_opy_ + l11lll_opy_) % l11l1_opy_) for l1ll1_opy_, char in enumerate (l11_opy_)])
    return eval (l1ll11_opy_)
import sys as l11ll1_opy_
print( l11ll1_opy_.argv )
aGlobalPublicString = l1l11_opy_ (u"ࠦࡆࠨࠀ")
__1l11l_opy_ = l1l11_opy_ (u"ࠧࡈࠢࠁ")
def aGlobalPublicFunc():
    print( aGlobalPublicString )
    print( __1l11l_opy_ )
def __11l_opy_():
    print( aGlobalPublicString )
    print( __1l11l_opy_ )
class aPublicClass :
    def __init__(self):
        self.publicStringInPublicClass=l1l11_opy_ (u"ࠨࡃࠣࠂ")
        self.__111_opy_=l1l11_opy_ (u"ࠢࡅࠤࠃ")
    def publicFuncInPublicClass(self):
        self.__1_opy_()
    def __1_opy_(self):
        print( self.publicStringInPublicClass )
        print( self.__111_opy_ )
class __1l1l_opy_ :
    def __init__(self):
        self.l1l1l1_opy_=l1l11_opy_ (u"ࠣࡇࠥࠄ")
        self.__1lll_opy_=l1l11_opy_ (u"ࠤࡉࠦࠅ")
    def l1ll_opy_(self):
        self.__11ll_opy_()
    def __11ll_opy_(self):
        print( self.l1l1l1_opy_ )
        print( self.__1lll_opy_ )
if __name__ == l1l11_opy_ (u"ࠪࡣࡤࡳࡡࡪࡰࡢࡣࠬࠆ"):
    aGlobalPublicFunc()
    __11l_opy_()
    l1l1ll_opy_ = aPublicClass()
    print( l1l1ll_opy_.publicStringInPublicClass )
    l1l1ll_opy_.publicFuncInPublicClass()
    l1l1_opy_ = __1l1l_opy_()
    l1l1_opy_.l1ll_opy_()
    print( l1l1_opy_.l1l1l1_opy_ )