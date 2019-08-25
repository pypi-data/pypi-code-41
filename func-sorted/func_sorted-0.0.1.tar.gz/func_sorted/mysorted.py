class MySorted():
    """
    自定义排序类
    """

    def __init__(self, list_tareget, ascending=True):
        self.__list_target = list_tareget
        self.__ascending = ascending

    @staticmethod
    def bubbling(listing, ascending=True):
        """
        冒泡法/反冒泡法排序
        :param listing:
        :param number:
        :return:
        """
        for i in range(len(listing) - 1):
            for n in range(len(listing) - i - 1):
                if listing[n] > listing[n + 1]:
                    listing[n], listing[n + 1] = \
                        listing[n + 1], listing[n]
        if ascending:
            return listing
        return listing[::-1]

    @staticmethod
    def choose(listing, ascending=True):
        """
        选择排序
        :param listing:
        :param ascending:
        :return:
        """
        for i in range(len(listing) - 1):
            min_index = i
            for n in range(i + 1, len(listing)):
                if listing[min_index] > listing[n]:
                    min_index = n
            temp = listing.pop(min_index)
            listing.insert(i, temp)
        if not ascending:
            return listing[::-1]
        return listing

    @staticmethod
    def inserted(listing, ascending=True):
        """
        插入排序
        :param listing:
        :param ascending:
        :return:
        """
        for i in range(1, len(listing)):
            x = listing[i]
            j = i
            while j > 0 and listing[j - 1] > x:
                listing[j] = listing[j - 1]
                j -= 1
            listing[j] = x
        if not ascending:
            return listing[::-1]
        return listing

    def __get_key(self, low, high):
        """
        获取快速排序的key值最终下标
        思想：1.随机找一个参考值key（此处取列表的第一个元素）
               将比key大的数抛到key值右边，比它小的抛到左边。
             2.如此就将列表分成两个部分，比key小的和比key大的两部分。
             3.再次以1中的方法对两个列表进行处理，会将列表划分4个部分
             4.如此循环最终得到排序好的列表
        :param low:
        :param high:
        :return:
        """
        key = self.__list_target[low]
        while low < high:
            if self.__ascending:
                # 遇到比key值小的将其抛到低位
                while low < high and self.__list_target[high] >= key:
                    high -= 1
                self.__list_target[low] = self.__list_target[high]
                # 遇到比key值大的将其抛到高位
                while low < high and self.__list_target[low] <= key:
                    low += 1
                self.__list_target[high] = self.__list_target[low]
            else:
                # 遇到比key值小的将其抛到低位
                while low < high and self.__list_target[high] <= key:
                    high -= 1
                self.__list_target[low] = self.__list_target[high]
                # 遇到比key值大的将其抛到高位
                while low < high and self.__list_target[low] >= key:
                    low += 1
                self.__list_target[high] = self.__list_target[low]
        self.__list_target[low] = key
        return low

    def __quick(self, low, high):
        """
        快速排序/使用递归方法实现
        :param low:
        :param high:
        :return:
        """
        if low < high:
            key = self.__get_key(low, high)
            self.__quick(low, key - 1)
            self.__quick(key + 1, high)
    @staticmethod
    def quick(listing, ascending=True):
        ms = MySorted(listing, ascending=ascending)
        ms.__quick(0,len(listing)-1)
        return ms.__list_target
# if __name__ == "__main__":
#     lis = [1, 25, 23, 4, 2, 5, 9, 66, 454, 2, 354, 1, 1, 1, 3, 3, 3, 2, 2, 2, 0, 0, 7, 85, 565, 565, 4, 77, 9, 64, 5,
#            45]
    # list01 = [4, 54, 458, 6, 4589, 1, 23, 4, 87, 5, 6, 45, 2, 887, 6, 0, 45, 6]
    # print(lis)
    # print('*' * 128)
    # print(MySorted.bubbling(lis))
    # print(MySorted.bubbling(lis,ascending=False))
    # print(MySorted.choose(lis))
    # print(MySorted.choose(lis,ascending=False))
    # print(MySorted.inserted(lis))
    # print(MySorted.inserted(lis,ascending=False))
    # 快速排序
    # ms = MySorted(lis,ascending=False)
    # ms.quick(0, len(lis) - 1)
    # print(ms.list_target)
    # print(MySorted.get_quick_result(lis))

class BinarySearch():
    """
    二分法查找列表元素类
    """
    def __init__(self):
        pass

    @staticmethod
    def binary_search(listing, element):
        """
        二分法查找
        :param listing:
        :param element:
        :return:
        """
        start = 0
        stop = len(listing) - 1
        while start <= stop:
            mid = (start + stop) // 2
            if listing[mid] > element:
                stop = mid - 1
            elif listing[mid] < element:
                start = mid + 1
            elif listing[mid] == element:
                # 找到元素后查看前一位是否也是该元素，
                # 找到满足条件的第一个位置索引
                while listing[mid] == element:
                    mid -= 1
                return mid + 1
        else:
            return 'The element %d is not exist!'%element

# if __name__ == "__main__":
#     data = [3,0,0,0,0,9,1,2,2,3,3,3,4,4,21,4,5,6,7,8,8,8,9,9,9,10,11,11,12,14,15,18]
#     res = MySorted.quick(data)
#     print(res)
#     r = BinarySearch.binary_search(res,20)
#     print(r)