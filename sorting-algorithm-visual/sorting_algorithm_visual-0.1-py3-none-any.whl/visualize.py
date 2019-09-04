import matplotlib.pyplot as plot
from sorting_algorithm_visual.sorting_algorithms import BubbleSort
import random

test = [random.randrange(0, 100) for _ in range(10)]
insertion_sort = BubbleSort(test)
sort_gen = insertion_sort.sort()

plot.ion()

graph = plot.bar([i for i, _ in enumerate(test)], test, color='blue')

plot.show()

while True:
    bar1, bar2 = next(sort_gen)
    for index, value in enumerate(insertion_sort.array):
        graph[index].set_height(value)
        graph[bar1].set_color('red')
        graph[bar2].set_color('red')

    plot.pause(.1)
    graph[bar1].set_color('blue')
    graph[bar2].set_color('blue')

