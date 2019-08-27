import matplotlib.pyplot as plt

# plt.plot([1.2, 1.3, 1.4, 1.5], [0.97322, 0.96319, 0.95462, 0.94729])
# plt.plot([1.2, 1.3, 1.4, 1.5], [0.94228, 0.92098, 0.90311, 0.88790])

# slopes = [1.5, 1.4, 1.3]
# axis_ratios = [0.5, 0.5, 0.5]
# values = [0.90856, 0.92109, 0.93576]
#
# # values_calc = list(map(lambda slope, axis_ratio : (2.0*slope)**0.5 * axis_ratio, slopes, axis_ratios))
# values_calc = list(map(lambda slope, axis_ratio : 0.5*(slope / 0.5)**0.5**0.5, slopes, axis_ratios))
#
# print(values)
# print(values_calc)
# print(list(map(lambda value, value_calc : value - value_calc, values, values_calc)))
# # plt.show()

slopes = [1.5, 0.5]
axis_ratios = [0.5, 0.5]
values = [0.86602, 1.1547]


# values_calc = list(map(lambda slope, axis_ratio : (2.0*slope)**0.5 * axis_ratio, slopes, axis_ratios))
values_calc = list(
    map(
        lambda slope, axis_ratio: (1 - axis_ratio ** 2.0) ** (slope - 1),
        slopes,
        axis_ratios,
    )
)

print(values)
print(values_calc)
print(list(map(lambda value, value_calc: value - value_calc, values, values_calc)))
# plt.show()
