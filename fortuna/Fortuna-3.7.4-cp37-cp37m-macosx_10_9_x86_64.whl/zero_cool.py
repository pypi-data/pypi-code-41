from Fortuna import ZeroCool, distribution_timer


def zero_cool_test(n):
    for method in ZeroCool.values():
        distribution_timer(method, n)


if __name__ == "__main__":
    zero_cool_test(11)
