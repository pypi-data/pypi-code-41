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
import random as l1l11ll_opy_
import l1111_opy_
import l11l1l_opy_
# l111l1_opy_ a list of l1l11ll_opy_ l1111_opy_
l1ll111_opy_ = [
    l1l11ll_opy_.choice (
        (l1111_opy_.l1l1_opy_, l1111_opy_.l111_opy_) # out of this tuple
    ) ()
    for index in range (10)
]
# l1l1l1l_opy_ them all walk a new l111l_opy_ with l1lll11_opy_ l1l11ll_opy_ l1ll11_opy_
for l1ll1l1_opy_ in l1ll111_opy_: # l1llll1_opy_ the l1l1ll1_opy_ for l1ll11l_opy_ human l1lll1l_opy_ in the list
    l1ll1l1_opy_.walk (
        l11l1l_opy_.l1l111_opy_ (
            l1l11ll_opy_.choice (
                (l11l1_opy_ (u"࡛ࠪࡷࡧࡦࡧࠩࠆ"), l11l1_opy_ (u"ࠫ࡜ࡵ࡯ࡧࡨࠪࠇ"), l11l1_opy_ (u"ࠬࡎ࡯ࡸ࡮ࠪࠈ"), l11l1_opy_ (u"࠭ࡋࡢ࡫࡬ࠫࠉ"), l11l1_opy_ (u"ࠧࡔࡪࡵࡩࡪࡱࠧࠊ")) # l1l1lll_opy_ this tuple of l1l1l11_opy_
            )
        )
    )