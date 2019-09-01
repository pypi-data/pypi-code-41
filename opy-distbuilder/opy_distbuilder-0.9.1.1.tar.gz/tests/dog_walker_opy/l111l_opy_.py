# coding: UTF-8
from sys import version_info as __1l1ll_opy_
l1_opy_ = __1l1ll_opy_[0] == 2
l11ll_opy_ = 2048
l1l11_opy_ = 7
def l1lll1_opy_ (l11l_opy_):
    global l111_opy_
    l1l_opy_ = ord (l11l_opy_ [-1])
    l1l1l_opy_ = l11l_opy_ [:-1]
    l11_opy_ = l1l_opy_ % len (l1l1l_opy_)
    l1ll11_opy_ = l1l1l_opy_ [:l11_opy_] + l1l1l_opy_ [l11_opy_:]
    if l1_opy_:
        l11l1_opy_ = l1111_opy_ () .join ([l1ll1_opy_ (ord (char) - l11ll_opy_ - (l1l1_opy_ + l1l_opy_) % l1l11_opy_) for l1l1_opy_, char in enumerate (l1ll11_opy_)])
    else:
        l11l1_opy_ = str () .join ([chr (ord (char) - l11ll_opy_ - (l1l1_opy_ + l1l_opy_) % l1l11_opy_) for l1l1_opy_, char in enumerate (l1ll11_opy_)])
    return eval (l11l1_opy_)
class l1llll_opy_:
    def walk (self, ll_opy_):
        print (l1lll1_opy_ (u"ࠫࡡࡴࡃ࡝ࠩࡰࡳࡳࠧࠧࠀ"))
        ll_opy_.l1ll1l_opy_ ()
class l1ll_opy_:
    def walk (self, ll_opy_):
        print (l1lll1_opy_ (u"ࠬࡢ࡮ࡃࡷࡪ࡫ࡪࡸࠠࡰࡨࡩࠥࠬࠁ")) # \n l1lll_opy_ start on new line
        ll_opy_.escape ()