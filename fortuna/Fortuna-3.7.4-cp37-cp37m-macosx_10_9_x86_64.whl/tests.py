import time as _time
import math as _math
import random as _random

from Fortuna import *
from fortuna_extras.range_tests import numeric_limits, range_tests


def quick_test():
    print("\nFortuna Quick Test")
    print("\nRandom Sequence Values:\n")
    start_test = _time.time()
    some_list = [i for i in range(10)]
    print(f"some_list = {some_list}\n")
    print("Base Case")
    distribution_timer(_random.choice, some_list, label="Random.choice(some_list)")
    distribution_timer(random_value, some_list, label="random_value(some_list)")
    truffle_shuffle = TruffleShuffle(some_list)
    distribution_timer(truffle_shuffle)
    some_tuple = tuple(i for i in range(10))
    monty = QuantumMonty(some_tuple)
    distribution_timer(monty)
    rand_value = RandomValue(some_list)
    distribution_timer(rand_value)

    print("\nWeighted Tables:\n")
    population = ("A", "B", "C", "D")
    cum_weights = (1, 3, 6, 10)
    rel_weights = (1, 2, 3, 4)
    cum_weighted_table = zip(cum_weights, population)
    rel_weighted_table = zip(rel_weights, population)
    print(f"population = {population}")
    print(f"cum_weights = {cum_weights}")
    print(f"rel_weights = {rel_weights}")
    print(f"cum_weighted_table = zip(cum_weights, population)")
    print(f"rel_weighted_table = zip(rel_weights, population)\n")
    print("Cumulative Base Case")
    distribution_timer(
        _random.choices, population, cum_weights=cum_weights,
        label="Random.choices(population, cum_weights=cum_weights)"
    )
    cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)
    distribution_timer(cum_weighted_choice)
    distribution_timer(
        cumulative_weighted_choice, tuple(zip(cum_weights, population)),
        label="cumulative_weighted_choice(tuple(zip(cum_weights, population)))"
    )

    print("Relative Base Case")
    distribution_timer(
        _random.choices, population, weights=rel_weights,
        label="Random.choices(population, weights=rel_weights)"
    )
    rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)
    distribution_timer(rel_weighted_choice)

    print("\nRandom Matrix Values:\n")
    some_matrix = {"A": (1, 2, 3, 4), "B": (10, 20, 30, 40), "C": (100, 200, 300, 400)}
    print(f"some_matrix = {some_matrix}\n")
    flex_cat = FlexCat(some_matrix, key_bias="flat_uniform", val_bias="flat_uniform")
    distribution_timer(flex_cat)

    print("\nRandom Integers:\n")
    print("Base Case")
    distribution_timer(_random.randrange, 10)
    distribution_timer(random_below, 10)
    distribution_timer(random_index, 10)
    distribution_timer(random_range, 10)
    distribution_timer(random_below, -10)
    distribution_timer(random_index, -10)
    distribution_timer(random_range, -10)
    print("Base Case")
    distribution_timer(_random.randrange, 1, 10)
    distribution_timer(random_range, 1, 10)
    distribution_timer(random_range, 10, 1)
    print("Base Case")
    distribution_timer(_random.randint, -5, 5)
    distribution_timer(random_int, -5, 5)
    print("Base Case")
    distribution_timer(_random.randrange, 1, 20, 2)
    distribution_timer(random_range, 1, 20, 2)
    distribution_timer(random_range, 1, 20, -2)
    distribution_timer(random_range, 20, 1, -2)
    distribution_timer(d, 10)
    distribution_timer(dice, 3, 6)
    distribution_timer(ability_dice, 4)
    distribution_timer(plus_or_minus, 5)
    distribution_timer(plus_or_minus_linear, 5)
    distribution_timer(plus_or_minus_gauss, 5)

    print("\nRandom Floats:\n")
    print("Base Case")
    distribution_timer(_random.random, post_processor=round)
    distribution_timer(canonical, post_processor=round)
    distribution_timer(random_float, 0.0, 10.0, post_processor=_math.floor)

    print("\nRandom Booleans:\n")
    distribution_timer(percent_true, 33.33)

    print("\nShuffle Performance:\n")
    shuffle_cycles = 8
    some_small_list = [i for i in range(10)]
    print("some_small_list = [i for i in range(10)]")
    some_med_list = [i for i in range(100)]
    print("some_med_list = [i for i in range(100)]")
    some_large_list = [i for i in range(1000)]
    print("some_large_list = [i for i in range(1000)]")
    print("\nBase Case:")
    print("Random.shuffle()")
    timer(_random.shuffle, some_small_list, cycles=shuffle_cycles)
    timer(_random.shuffle, some_med_list, cycles=shuffle_cycles)
    timer(_random.shuffle, some_large_list, cycles=shuffle_cycles)
    some_med_list.sort()
    print("\nTest Case 1:")
    print("Fortuna.fisher_yates()")
    timer(fisher_yates, some_small_list, cycles=shuffle_cycles)
    timer(fisher_yates, some_med_list, cycles=shuffle_cycles)
    timer(fisher_yates, some_large_list, cycles=shuffle_cycles)
    some_med_list.sort()
    print("\nTest Case 2:")
    print("Fortuna.knuth()")
    timer(knuth, some_small_list, cycles=shuffle_cycles)
    timer(knuth, some_med_list, cycles=shuffle_cycles)
    timer(knuth, some_large_list, cycles=shuffle_cycles)
    some_med_list.sort()
    print("\nTest Case 3:")
    print("Fortuna.shuffle() knuth_b algorithm")
    timer(shuffle, some_small_list, cycles=shuffle_cycles)
    timer(shuffle, some_med_list, cycles=shuffle_cycles)
    timer(shuffle, some_large_list, cycles=shuffle_cycles)
    print("\n")

    print("-" * 73)
    stop_test = _time.time()
    print(f"Total Test Time: {round(stop_test - start_test, 3)} seconds")


if __name__ == "__main__":
    print("\nFortuna Test Suite: RNG Storm Engine\n")
    numeric_limits()
    range_tests()
    print(f"\n{'-' * 73}")
    test_warm_up()
    quick_test()
