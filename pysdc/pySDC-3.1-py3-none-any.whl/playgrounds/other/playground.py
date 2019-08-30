import sys
import numpy as np

def main():

    def modify(my_list_active, pos):
        for l in my_list_active:
            l[pos] = 99

    list = [np.arange(i) for i in range(1, 1000)]
    print(list[0], list[1], list[2], sys.getsizeof(list))

    list_active = [l for l in list if 2 <= len(l) <= 500]

    list_active_2 = [l for l in list_active if len(l) <= 3]

    modify(list_active, 0)
    print(list[0], list[1], list[2], sys.getsizeof(list))
    modify(list_active, 1)
    print(list[0], list[1], list[2], sys.getsizeof(list))

    print(list[1] is list_active[0], list[2] is list_active[1])
    print(list[1] is list_active_2[0], list[2] is list_active_2[1])



if __name__ == '__main__':
    main()