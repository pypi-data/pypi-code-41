from Fortuna import *


test_warm_up(128)
print("\nRandomValue Strings:\n")

gen_f_string = RandomValue((
    f"A. d(2) = {d(2)}",
    f"B. d(2) = {d(2)}",
    f"C. d(2) = {d(2)}",
    f"D. d(2) = {d(2)}",
    f"E. d(2) = {d(2)}",
))

gen_dynamic_string = RandomValue((
    lambda: f"A. d(2) = {d(2)}",
    lambda: f"B. d(2) = {d(2)}",
    lambda: f"C. d(2) = {d(2)}",
    lambda: f"D. d(2) = {d(2)}",
    lambda: f"E. d(2) = {d(2)}",
))

gen_higher_order_string = RandomValue((
    lambda f, x, y: f"A. f(x, y) = {f(x, y)}",
    lambda f, x, y: f"B. f(x, y) = {f(x, y)}",
    lambda f, x, y: f"C. f(x, y) = {f(x, y)}",
    lambda f, x, y: f"D. f(x, y) = {f(x, y)}",
    lambda f, x, y: f"E. f(x, y) = {f(x, y)}",
))

distribution_timer(gen_f_string, label="gen_f_string()")
distribution_timer(gen_dynamic_string, label="gen_dynamic_string()")
distribution_timer(gen_dynamic_string, range_to=3, label="gen_dynamic_string(range_to=3): First 3 lambdas (A-C)")
distribution_timer(gen_dynamic_string, range_to=-3, label="gen_dynamic_string(range_to=-3): Last 3 lambdas (C-E)")
distribution_timer(gen_dynamic_string, zero_cool=front_linear, label="gen_dynamic_string(zero_cool=front_linear)")
distribution_timer(gen_higher_order_string, f=dice, x=2, y=2, label="gen_higher_order_string(f=dice, x=2, y=2)")

distribution_timer(
    gen_higher_order_string,    # RandomValue generator
    f=random_int, x=-1, y=1,    # lambda arguments
    zero_cool=back_linear,      # distribution type, function must follow ZeroCool spec
    range_to=-4,                # distribution limiter, Defaults to N, must be in range [-N, N] with N = len(data)
    label="The Kitchen Sink"    # label for the distribution_timer
)
