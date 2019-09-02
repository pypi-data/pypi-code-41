import itertools


def cartesian_product(*lists):
    prod = []

    for i in itertools.product(*lists):
        prod.append(i)

    return prod
