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
import l1ll1_opylib_
import l11l11_opylib_
l11111_opylib_ = l11l11_opylib_.l111ll_opylib_ (l1lll1_opylib_ (u"ࠨ࡙ࡵࡥ࡫࡬ࠧࠄ"))
l1llll1_opylib_ = l11l11_opylib_.l111ll_opylib_ (l1lll1_opylib_ (u"ࠩࡋࡳࡼࡲࠧࠅ"))
you = l1ll1_opylib_.l1lll_opylib_ ()
l1lllll_opylib_ = l1ll1_opylib_.l1ll1l_opylib_ () # l1lll1l_opylib_ your l1111l_opylib_
you.walk (l11111_opylib_)
l1lllll_opylib_.walk (l1llll1_opylib_)