# coding: UTF-8
from sys import version_info as __11_opylib_
l1_opylib_ = __11_opylib_[0] == 2
l1ll_opylib_ = 2048
l1ll1l_opylib_ = 7
def l11l1_opylib_ (ll_opylib_):
    global l1l_opylib_
    l1l1l_opylib_ = ord (ll_opylib_ [-1])
    l11l_opylib_ = ll_opylib_ [:-1]
    l1llll_opylib_ = l1l1l_opylib_ % len (l11l_opylib_)
    l1l11_opylib_ = l11l_opylib_ [:l1llll_opylib_] + l11l_opylib_ [l1llll_opylib_:]
    if l1_opylib_:
        l1lll1_opylib_ = unicode () .join ([unichr (ord (char) - l1ll_opylib_ - (l11ll_opylib_ + l1l1l_opylib_) % l1ll1l_opylib_) for l11ll_opylib_, char in enumerate (l1l11_opylib_)])
    else:
        l1lll1_opylib_ = str () .join ([chr (ord (char) - l1ll_opylib_ - (l11ll_opylib_ + l1l1l_opylib_) % l1ll1l_opylib_) for l11ll_opylib_, char in enumerate (l1l11_opylib_)])
    return eval (l1lll1_opylib_)
class l1l1_opylib_:
    def walk (self, l111l_opylib_):
        print (l11l1_opylib_ (u"ࠫࡡࡴࡃ࡝ࠩࡰࡳࡳࠧࠧࠀ"))
        l111l_opylib_.l1ll1_opylib_ ()
class l111_opylib_:
    def walk (self, l111l_opylib_):
        print (l11l1_opylib_ (u"ࠬࡢ࡮ࡃࡷࡪ࡫ࡪࡸࠠࡰࡨࡩࠥࠬࠁ")) # \n l1lll_opylib_ start on new line
        l111l_opylib_.escape ()