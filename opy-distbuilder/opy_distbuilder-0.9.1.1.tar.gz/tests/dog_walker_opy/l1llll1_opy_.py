# coding: UTF-8
from sys import version_info as __1lll_opy_
ll_opy_ = __1lll_opy_[0] == 2
l1ll11_opy_ = 2048
l111l_opy_ = 7
def l1l1ll_opy_ (l111_opy_):
    global l11ll_opy_
    l11_opy_ = ord (l111_opy_ [-1])
    l1l11_opy_ = l111_opy_ [:-1]
    l1_opy_ = l11_opy_ % len (l1l11_opy_)
    l1ll1l_opy_ = l1l11_opy_ [:l1_opy_] + l1l11_opy_ [l1_opy_:]
    if ll_opy_:
        l1l1_opy_ = l1lll1_opy_ () .join ([l1ll1_opy_ (ord (char) - l1ll11_opy_ - (l1111_opy_ + l11_opy_) % l111l_opy_) for l1111_opy_, char in enumerate (l1ll1l_opy_)])
    else:
        l1l1_opy_ = str () .join ([chr (ord (char) - l1ll11_opy_ - (l1111_opy_ + l11_opy_) % l111l_opy_) for l1111_opy_, char in enumerate (l1ll1l_opy_)])
    return eval (l1l1_opy_)
import l11l_opy_
import l11l1l_opy_
l1lll1l_opy_ = l11l1l_opy_.l11lll_opy_ (l1l1ll_opy_ (u"ࠨ࡙ࡵࡥ࡫࡬ࠧࠄ"))
l111l1_opy_ = l11l1l_opy_.l11lll_opy_ (l1l1ll_opy_ (u"ࠩࡋࡳࡼࡲࠧࠅ"))
you = l11l_opy_.l1llll_opy_ ()
l11111_opy_ = l11l_opy_.l11l1_opy_ () # l1lllll_opy_ your l1111l_opy_
you.walk (l1lll1l_opy_)
l11111_opy_.walk (l111l1_opy_)