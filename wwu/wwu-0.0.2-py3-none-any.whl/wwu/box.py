from itertools import permutations
from math import floor


class Box:
    def __init__(self, height: float, width: float, depth: float):
        self.dimensions = (height, width, depth)

    def wwu(self, height: float, width: float, depth: float) -> int:
        """ 
        Supplied with the storage dimensions will return the optimal permutation for
        storing a box.
        """
        perms = []
        for perm in permutations(self.dimensions):
            # We want floored values here because boxes are solid objects.
            perms.append(
                floor(height / perm[0])
                * floor(width / perm[1])
                * floor(depth / perm[2])
            )
        if sum(perms) > 0:
            return perms.index(max(perms))
        else:  # If the box does not fit.
            raise ZeroDivisionError("Box will not fit in storage.")
