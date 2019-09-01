# coding: UTF-8
from sys import version_info as __1lll1_opy_
l1lll_opy_ = __1lll1_opy_[0] == 2
l1l_opy_ = 2048
l1ll1l_opy_ = 7
def l11l_opy_ (l11ll_opy_):
    global l11l1_opy_
    l1llll_opy_ = ord (l11ll_opy_ [-1])
    l1_opy_ = l11ll_opy_ [:-1]
    l1l11_opy_ = l1llll_opy_ % len (l1_opy_)
    l111l_opy_ = l1_opy_ [:l1l11_opy_] + l1_opy_ [l1l11_opy_:]
    if l1lll_opy_:
        l1l1l_opy_ = l1ll_opy_ () .join ([l1l1ll_opy_ (ord (char) - l1l_opy_ - (l111_opy_ + l1llll_opy_) % l1ll1l_opy_) for l111_opy_, char in enumerate (l111l_opy_)])
    else:
        l1l1l_opy_ = str () .join ([chr (ord (char) - l1l_opy_ - (l111_opy_ + l1llll_opy_) % l1ll1l_opy_) for l111_opy_, char in enumerate (l111l_opy_)])
    return eval (l1l1l_opy_)
import random as l1ll1l1_opy_
import l11_opy_
import l11l11_opy_
# l11111_opy_ a list of l1ll1l1_opy_ l11_opy_
l1ll111_opy_ = [
    l1ll1l1_opy_.choice (
        (l11_opy_.l1111_opy_, l11_opy_.l1ll11_opy_) # out of this tuple
    ) ()
    for index in range (10)
]
# l1lll11_opy_ them all walk a new l1ll1_opy_ with l1l1ll1_opy_ l1ll1l1_opy_ l111ll_opy_
for l1l1lll_opy_ in l1ll111_opy_: # l1l1l11_opy_ the l1ll1ll_opy_ for l1l11l1_opy_ human l1l11ll_opy_ in the list
    l1l1lll_opy_.walk (
        l11l11_opy_.l11l1l_opy_ (
            l1ll1l1_opy_.choice (
                (l11l_opy_ (u"࡛ࠪࡷࡧࡦࡧࠩࠆ"), l11l_opy_ (u"ࠫ࡜ࡵ࡯ࡧࡨࠪࠇ"), l11l_opy_ (u"ࠬࡎ࡯ࡸ࡮ࠪࠈ"), l11l_opy_ (u"࠭ࡋࡢ࡫࡬ࠫࠉ"), l11l_opy_ (u"ࠧࡔࡪࡵࡩࡪࡱࠧࠊ")) # l1l1l1l_opy_ this tuple of l1l111l_opy_
            )
        )
    )