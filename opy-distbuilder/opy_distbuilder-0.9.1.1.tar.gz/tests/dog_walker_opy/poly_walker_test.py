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
import random as l1ll111_opy_
import l11l_opy_
import l11l1l_opy_
# l1lllll_opy_ a list of l1ll111_opy_ l11l_opy_
l11ll1l_opy_ = []
for index in range (10):
    l11ll1l_opy_.append (
        l1ll111_opy_.choice ((l11l_opy_.l1llll_opy_, l11l_opy_.l11l1_opy_)) () # l1l1111_opy_ l11llll_opy_ l11ll11_opy_ class
    )
# l1ll1ll_opy_ them all walk a new l1l_opy_ with l1l1lll_opy_ l1ll111_opy_ l1l11l_opy_
for l11lll1_opy_ in l11ll1l_opy_:
    l11lll1_opy_.walk (
        l11l1l_opy_.l11lll_opy_ (
            l1ll111_opy_.choice (
                (l1l1ll_opy_ (u"ࠨ࡙ࡵࡥ࡫࡬ࠧࠋ"), l1l1ll_opy_ (u"࡚ࠩࡳࡴ࡬ࡦࠨࠌ"), l1l1ll_opy_ (u"ࠪࡌࡴࡽ࡬ࠨࠍ"), l1l1ll_opy_ (u"ࠫࡐࡧࡩࡪࠩࠎ"), l1l1ll_opy_ (u"࡙ࠬࡨࡳࡧࡨ࡯ࠬࠏ")) # l1l11ll_opy_ this tuple of l1l111l_opy_
            )
        )
    )