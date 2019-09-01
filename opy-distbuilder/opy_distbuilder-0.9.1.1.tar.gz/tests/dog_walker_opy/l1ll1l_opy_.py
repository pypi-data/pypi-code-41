# coding: UTF-8
from sys import version_info as __1l_opy_
l1l1_opy_ = __1l_opy_[0] == 2
l1l1l_opy_ = 2048
l1ll_opy_ = 7
def l1ll1_opy_ (ll_opy_):
    global l111l_opy_
    l1llll_opy_ = ord (ll_opy_ [-1])
    l111_opy_ = ll_opy_ [:-1]
    l11ll_opy_ = l1llll_opy_ % len (l111_opy_)
    l11_opy_ = l111_opy_ [:l11ll_opy_] + l111_opy_ [l11ll_opy_:]
    if l1l1_opy_:
        l1_opy_ = l1lll1_opy_ () .join ([l11l1_opy_ (ord (char) - l1l1l_opy_ - (l1111_opy_ + l1llll_opy_) % l1ll_opy_) for l1111_opy_, char in enumerate (l11_opy_)])
    else:
        l1_opy_ = str () .join ([chr (ord (char) - l1l1l_opy_ - (l1111_opy_ + l1llll_opy_) % l1ll_opy_) for l1111_opy_, char in enumerate (l11_opy_)])
    return eval (l1_opy_)
class l1lll_opy_:
    def walk (self, l1l1ll_opy_):
        print (l1ll1_opy_ (u"ࠫࡡࡴࡃ࡝ࠩࡰࡳࡳࠧࠧࠀ"))
        l1l1ll_opy_.l11l_opy_ ()
class l1l11_opy_:
    def walk (self, l1l1ll_opy_):
        print (l1ll1_opy_ (u"ࠬࡢ࡮ࡃࡷࡪ࡫ࡪࡸࠠࡰࡨࡩࠥࠬࠁ")) # \n l1ll11_opy_ start on new line
        l1l1ll_opy_.escape ()