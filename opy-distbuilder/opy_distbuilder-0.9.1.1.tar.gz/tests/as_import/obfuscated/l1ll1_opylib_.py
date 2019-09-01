# coding: UTF-8
from sys import version_info as __1ll_opylib_
l11ll_opylib_ = __1ll_opylib_[0] == 2
l11l1_opylib_ = 2048
l1_opylib_ = 7
def l1lll1_opylib_ (l1ll11_opylib_):
    global l1l1ll_opylib_
    l1l1l_opylib_ = ord (l1ll11_opylib_ [-1])
    l11l_opylib_ = l1ll11_opylib_ [:-1]
    l1l11_opylib_ = l1l1l_opylib_ % len (l11l_opylib_)
    l111l_opylib_ = l11l_opylib_ [:l1l11_opylib_] + l11l_opylib_ [l1l11_opylib_:]
    if l11ll_opylib_:
        l1111_opylib_ = l1llll_opylib_ () .join ([l111_opylib_ (ord (char) - l11l1_opylib_ - (l1l1_opylib_ + l1l1l_opylib_) % l1_opylib_) for l1l1_opylib_, char in enumerate (l111l_opylib_)])
    else:
        l1111_opylib_ = str () .join ([chr (ord (char) - l11l1_opylib_ - (l1l1_opylib_ + l1l1l_opylib_) % l1_opylib_) for l1l1_opylib_, char in enumerate (l111l_opylib_)])
    return eval (l1111_opylib_)
class l1lll_opylib_:
    def walk (self, l1l_opylib_):
        print (l1lll1_opylib_ (u"ࠫࡡࡴࡃ࡝ࠩࡰࡳࡳࠧࠧࠀ"))
        l1l_opylib_.l11_opylib_ ()
class l1ll1l_opylib_:
    def walk (self, l1l_opylib_):
        print (l1lll1_opylib_ (u"ࠬࡢ࡮ࡃࡷࡪ࡫ࡪࡸࠠࡰࡨࡩࠥࠬࠁ")) # \n ll_opylib_ start on new line
        l1l_opylib_.escape ()