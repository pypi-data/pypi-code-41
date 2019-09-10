from typing import List


def is_prefix_code(words: List[str]) -> bool:
    """Return bool representing if given words are a prefix code.
        words:List[str], the list of words from the code.
    """
    for i, w1 in enumerate(words):
        for j, w2 in enumerate(words):
            if i != j and w1.startswith(w2):
                return False
    return True


def mcmillan_sum(words: List[str]) -> float:
    """Return sum of diadicts as specified in kraft-mcmillan theorem.
        words:List[str], the list of words from the code.
    """
    return sum([2**(-len(w)) for w in words])


def is_complete_prefix_code(words: List[str]) -> bool:
    """Return bool representing if given words are a complete prefix code.
        words:List[str], the list of words from the code.
    """
    return is_prefix_code(words) and mcmillan_sum(words) == 1
