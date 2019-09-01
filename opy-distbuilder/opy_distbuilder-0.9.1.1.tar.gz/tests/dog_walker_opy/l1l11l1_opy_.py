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
import random as l1lll11_opy_
import l1ll1l_opy_
import l1l11l_opy_
# l11111_opy_ a list of l1lll11_opy_ l1ll1l_opy_
l1l111l_opy_ = [
    l1lll11_opy_.choice (
        (l1ll1l_opy_.l1lll_opy_, l1ll1l_opy_.l1l11_opy_) # out of this tuple
    ) ()
    for index in range (10)
]
# l1l1lll_opy_ them all walk a new l1l1ll_opy_ with l1ll111_opy_ l1lll11_opy_ l1l111_opy_
for l1l11ll_opy_ in l1l111l_opy_: # l1ll11l_opy_ the l1l1l1l_opy_ for l1ll1ll_opy_ human l1ll1l1_opy_ in the list
    l1l11ll_opy_.walk (
        l1l11l_opy_.l11lll_opy_ (
            l1lll11_opy_.choice (
                (l1ll1_opy_ (u"࡛ࠪࡷࡧࡦࡧࠩࠆ"), l1ll1_opy_ (u"ࠫ࡜ࡵ࡯ࡧࡨࠪࠇ"), l1ll1_opy_ (u"ࠬࡎ࡯ࡸ࡮ࠪࠈ"), l1ll1_opy_ (u"࠭ࡋࡢ࡫࡬ࠫࠉ"), l1ll1_opy_ (u"ࠧࡔࡪࡵࡩࡪࡱࠧࠊ")) # l1l1l11_opy_ this tuple of l1l1ll1_opy_
            )
        )
    )