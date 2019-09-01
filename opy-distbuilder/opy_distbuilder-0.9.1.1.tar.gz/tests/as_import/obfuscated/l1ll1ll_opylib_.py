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
import random
import l1111_opylib_
import l11l1l_opylib_
# l111l1_opylib_ a list of random l1111_opylib_
l1ll111_opylib_ = [
    random.choice (
        (l1111_opylib_.l1l1_opylib_, l1111_opylib_.l111_opylib_) # out of this tuple
    ) ()
    for index in range (10)
]
# l1l1l1l_opylib_ them all walk a new l111l_opylib_ with l1lll11_opylib_ random l1ll11_opylib_
for l1ll1l1_opylib_ in l1ll111_opylib_: # l1llll1_opylib_ the l1l1ll1_opylib_ for l1ll11l_opylib_ human l1lll1l_opylib_ in the list
    l1ll1l1_opylib_.walk (
        l11l1l_opylib_.l1l111_opylib_ (
            random.choice (
                (l11l1_opylib_ (u"࡛ࠪࡷࡧࡦࡧࠩࠆ"), l11l1_opylib_ (u"ࠫ࡜ࡵ࡯ࡧࡨࠪࠇ"), l11l1_opylib_ (u"ࠬࡎ࡯ࡸ࡮ࠪࠈ"), l11l1_opylib_ (u"࠭ࡋࡢ࡫࡬ࠫࠉ"), l11l1_opylib_ (u"ࠧࡔࡪࡵࡩࡪࡱࠧࠊ")) # l1l1lll_opylib_ this tuple of l1l1l11_opylib_
            )
        )
    )