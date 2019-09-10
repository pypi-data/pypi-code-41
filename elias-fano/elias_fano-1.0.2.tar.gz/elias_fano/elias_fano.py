from typing import List
from unary_coding import inverted_unary
from math import ceil, log2


class EliasFano:
    def __init__(self, numbers: List[int]):
        """Initialize a new EliasFano data structure for given monotone sequence.
            numbers:List[int], sequence to convert into an EliasFano data structure.
        """
        self._size = ceil(log2(max(numbers)/len(numbers)))
        superiors, inferiors = list(zip(*[
            divmod(n, 1 << self._size) for n in numbers
        ]))
        self._inferiors = "".join([
            f"{{0:0{self._size}b}}".format(n) for n in inferiors
        ])
        self._superiors = "".join([
            inverted_unary(n - superiors[i-1] if i else n)
            for i, n in enumerate(superiors)
        ])

    def _get_inferior(self, k: int) -> int:
        return int(self._inferiors[self._size*k:self._size*(k+1)], 2)

    def selection(self, k: int) -> int:
        """Return k-th integer stored within current EliasFano data structure.
            k:int, index of integer to be reconstructed.
        """
        zeros = 0
        inferior = self._get_inferior(k)
        for c in self._superiors:
            if c == "0":
                zeros += 1
            else:
                k -= 1
            if k == -1:
                break
        return (zeros << self._size) + inferior

    def rank(self, p: int) -> int:
        """Return index for given integer p.
            k:int, index of integer to be reconstructed.
        """
        k = -1
        sup, inf = divmod(p, 1 << self._size)
        for c in self._superiors:
            if c == "0":
                sup -= 1
            else:
                k += 1
                if sup == 0 and inf == self._get_inferior(k):
                    return k

        raise ValueError(f"Given element {p} does not exist in structure.")
