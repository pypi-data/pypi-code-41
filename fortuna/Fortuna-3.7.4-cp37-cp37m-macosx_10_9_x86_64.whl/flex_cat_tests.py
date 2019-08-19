from Fortuna import *


def flex_cat_tests():
    print("\nFlexCat Test Suite\n")

    my_matrix = {
        "A": (1, 2, 3),
        "B": (10, 20, 30),
        "C": (100, 200, 300),
    }

    zero_cool_methods = (
        "front_linear", "middle_linear", "back_linear", "quantum_linear",
        "front_gauss", "middle_gauss", "back_gauss", "quantum_gauss",
        "front_poisson", "middle_poisson", "back_poisson", "quantum_poisson",
        "quantum_monty", "flat_uniform",
    )

    for v_bias in zero_cool_methods:
        for k_bias in zero_cool_methods:
            my_flex_cat = FlexCat(my_matrix, key_bias=k_bias, val_bias=v_bias)
            distribution_timer(my_flex_cat, num_cycles=1000)


def lambda_flex_cat_tests():
    print("\nFlexCat Test Suite\n")

    my_matrix = {
        "A": (
            lambda x: f"A1: {d(x)}",
            lambda x: f"A2: {d(x)}",
            lambda x: f"A3: {d(x)}",
        ),
        "B": (
            lambda x: f"B1: {d(x)}",
            lambda x: f"B2: {d(x)}",
            lambda x: f"B3: {d(x)}",
        ),
        "C": (
            lambda x: f"C1: {d(x)}",
            lambda x: f"C2: {d(x)}",
            lambda x: f"C3: {d(x)}",
        ),
    }

    zero_cool_methods = ("flat_uniform", "front_linear", "front_gauss", "front_poisson", "quantum_monty")

    for v_bias in zero_cool_methods:
        my_flex_cat = FlexCat(my_matrix, val_bias=v_bias)
        distribution_timer(my_flex_cat, x=4, num_cycles=1000000)


if __name__ == "__main__":
    # flex_cat_tests()
    lambda_flex_cat_tests()
