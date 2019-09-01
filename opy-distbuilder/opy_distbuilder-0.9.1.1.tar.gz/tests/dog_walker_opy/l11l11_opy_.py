# coding: UTF-8
from sys import version_info as __11_opy_
l1_opy_ = __11_opy_[0] == 2
l1ll_opy_ = 2048
l1ll1l_opy_ = 7
def l11l1_opy_ (ll_opy_):
    global l1l_opy_
    l1l1l_opy_ = ord (ll_opy_ [-1])
    l11l_opy_ = ll_opy_ [:-1]
    l1llll_opy_ = l1l1l_opy_ % len (l11l_opy_)
    l1l11_opy_ = l11l_opy_ [:l1llll_opy_] + l11l_opy_ [l1llll_opy_:]
    if l1_opy_:
        l1lll1_opy_ = unicode () .join ([unichr (ord (char) - l1ll_opy_ - (l11ll_opy_ + l1l1l_opy_) % l1ll1l_opy_) for l11ll_opy_, char in enumerate (l1l11_opy_)])
    else:
        l1lll1_opy_ = str () .join ([chr (ord (char) - l1ll_opy_ - (l11ll_opy_ + l1l1l_opy_) % l1ll1l_opy_) for l11ll_opy_, char in enumerate (l1l11_opy_)])
    return eval (l1lll1_opy_)
import l1111_opy_
import l11l1l_opy_
l11111_opy_ = l11l1l_opy_.l1l111_opy_ (l11l1_opy_ (u"ࠨ࡙ࡵࡥ࡫࡬ࠧࠄ"))
l1111l_opy_ = l11l1l_opy_.l1l111_opy_ (l11l1_opy_ (u"ࠩࡋࡳࡼࡲࠧࠅ"))
you = l1111_opy_.l1l1_opy_ ()
l111ll_opy_ = l1111_opy_.l111_opy_ () # l111l1_opy_ your l1lllll_opy_
you.walk (l11111_opy_)
l111ll_opy_.walk (l1111l_opy_)