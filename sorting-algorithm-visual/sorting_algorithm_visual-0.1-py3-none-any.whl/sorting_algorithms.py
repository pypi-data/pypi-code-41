import random


class SortingAlgorithm:
    def __init__(self, array=[0]):
        self.array = array
        self.swapped = None

    def swap(self, index1, index2):
        self.array[index1], self.array[index2] = self.array[index2], self.array[index1]
        return self

    def sort(self):
        pass


class InsertionSort(SortingAlgorithm):
    def sort(self):
        """
        This is a generator function which yields the indices of two swapped values in an array of integers

        Sorts the array by looking at pairs of values, swapping them based on their value, backtracking until the
        there is no need to swap. It will then return to the point when it had come furthest along
        :return: yields the index of the swapped elements
        """
        index = 0
        highpoint = 0
        while index < len(self.array) - 1:
            if self.array[index] > self.array[index + 1]:
                self.swap(index, index + 1)
                if index > 0:
                    index -= 1
            else:
                index += 1
                if index > highpoint:
                    highpoint = index
                else:
                    index = highpoint
            yield index, index + 1


class SelectionSort(SortingAlgorithm):
    def sort(self):
        index = 0
        lowest_index = 0
        current = 0
        while current < len(self.array) - 1:
            while index < len(self.array):
                if self.array[index] < self.array[lowest_index]:
                    lowest_index = index

                yield current, index
                index += 1
            self.swap(current, lowest_index)
            current += 1
            lowest_index = current
            index = current

            yield current, lowest_index


class BubbleSort(SortingAlgorithm):
    def sort(self):
        index = 0
        count = 0
        swaps = 0
        done = False
        while not done:
            while index < len(self.array) - count:
                if self.array[index] > self.array[index + 1]:
                    self.swap(index, index + 1)
                    swaps += 1
                yield index, index+1
                index += 1
            count += 1
            index = 0
            if swaps == 0:
                done = True
            swaps = 0


class RandomSort(SortingAlgorithm):
    def sort(self):
        while(True):
            index1 = random.randrange(0, len(self.array))
            index2 = random.randrange(0, len(self.array))

            self.swap(index1, index2)

            yield index1, index2
