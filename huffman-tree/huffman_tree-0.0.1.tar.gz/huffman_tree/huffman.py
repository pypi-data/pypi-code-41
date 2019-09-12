import sys
import os


class Node:
    def __init__(self, char, value, left, right):
        self.char = char
        self.value = value
        self.left = left
        self.right = right
    def print_tree(self):
        print(self.char, end=' ')
        if self.left:
            self.left.print_tree()
        if self.right:
            self.right.print_tree()

class Node_queue:
    def __init__(self, node_list):
        self.node_list = node_list
        self.size = len(self.node_list)

    def is_empty(self):
        return self.size == 0

    def pop(self):
        self.size -= 1
        return self.node_list[self.size]

    def top(self):
        return self.node_list[self.size - 1]

    def add_node(self, node):
        self.node_list[self.size] = node
        self.size += 1
        cursor = self.size - 1
        while cursor != 0:
            if self.node_list[cursor].value >= self.node_list[cursor - 1].value:
                temp = self.node_list[cursor]
                self.node_list[cursor] = self.node_list[cursor - 1]
                self.node_list[cursor - 1] = temp
                cursor -= 1
            else:
                return

class Huffman:
    def __init__(self, frequency_dict):
        sorted_list = sorted(frequency_dict.items(), key=lambda kv: kv[1])
        node_list = [Node(sorted_list[i][0], sorted_list[i][1], None, None) for i in range(len(sorted_list)-1, -1, -1)]
        node_queue = Node_queue(node_list)
        self.node_queue = node_queue

    def build(self):
        while self.node_queue.size > 1:
            left_node = self.node_queue.pop()
            right_node = self.node_queue.pop()
            new_node = Node(
                left_node.char + right_node.char,
                left_node.value + right_node.value,
                left_node,
                right_node
            )
            self.node_queue.add_node(new_node)

    def print_tree(self):
        self.node_queue.top().print_tree()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("no input file.")

    filename = sys.argv[1]

    if not os.path.isfile(filename):
        raise Exception(filename + ' does not exist.')

    with open(filename) as file:
        frequency_dict = {}
        chars = file.read(512)

        while len(chars) != 0:
            for char in chars:
                if char not in frequency_dict:
                    frequency_dict[char] = 1
                else:
                    frequency_dict[char] += 1
            chars = file.read(512)

    print(frequency_dict)
    huffman_tree = Huffman(frequency_dict)
    huffman_tree.build()
    huffman_tree.print_tree()
    
