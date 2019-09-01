from collections import defaultdict
from itertools import islice, product


class ThreadsManager:
    '''A helper class used to keep track of different threads in graph. Needed
    to build cycles if neccessary.
    '''
    def __init__(self, dicts=list()):
        self.threads = list()
        for d in dicts:
            self.load_from_dict(d)

    def load_from_dict(self, d: dict, reverse=False):
        for a, to_nodes in d.items():
            for b in to_nodes:
                if not reverse:
                    self.connect_nodes(a, b)
                else:
                    self.connect_nodes(b, a)

    def add_node(self, node: str):
        for thread in self.find_threads(node):
            return
        self.threads.append([node])

    def connect_nodes(self, a, b):
        '''Connects a to b'''
        list_a = list(self.find_threads(a, True))
        list_b = list(self.find_threads(b, True))
        if list_a and list_b:
            to_delete = set()
            for i, j in product(list_a, list_b):
                thread_a, thread_b = self.threads[i], self.threads[j]
                n, m = thread_a.index(a), thread_b.index(b)
                lt_a = thread_a[:n + 1]
                lt_b = thread_b[m:]
                lt = lt_a.extend(lt_b)
                if lt not in self.threads:
                    if n == len(thread_a) - 1:
                        to_delete.add(n)
                    if m == 0:
                        to_delete.add(m)
                    self.threads.append(lt)
            self.threads = [t for i, t in enumerate(self.threads)
                            if i not in to_delete]                        
        elif list_a:
            for i in list_a:
                thread = self.threads[i]
                if thread[-1] == a:
                    thread.append(b)
                else:
                    k = thread.index(a)
                    lt = thread[:k + 1]
                    lt.append(b)
                    if lt not in self.threads:
                        self.threads.append(lt)
        elif list_b:
            for i in list_b:
                thread = self.threads[i]
                k = thread.index(b)
                if k == 0:
                    thread.insert(0, a)
                else:
                    lt = [a] + thread[k:]
                    if lt not in self.threads:
                        self.threads.append(lt)
        else:
            self.threads.append([a, b])

    def connect_nodes2(self, a: str, b: str):
        '''Connects a to b. '''
        is_var_present = False
        for thread in islice(self.threads, len(self.threads)):
            if a in thread:
                is_var_present = True
                if thread[-1] == a:
                    thread.append(b)
                else:
                    i = thread.index(a)
                    lt = thread[:i + 1]
                    lt.append(b)
                    # When cycles are present duplicates are possible.
                    if lt not in self.threads:
                        self.threads.append(lt)
            elif thread[0] == b:
                is_var_present = True
                thread.insert(0, a)
        if not is_var_present:
            self.threads.append([a, b])

    def find_threads(self, node: str, inds=False):
        for i, thread in enumerate(self.threads):
            if node in thread:
                yield i if inds else thread

    def translate_to_dict(self):
        d = defaultdict(set)
        for thread in self.threads:
            it = iter(thread)
            prev = next(it)
            for v in it:
                d[v].add(prev)
                prev = v
        return dict(d)

    def get_node_order(self, node: str):
        return max(thread.index(node) for thread in self.find_threads(node))

    def get_confluent_path(self, source_node: str):
        if source_node:
            threads = [thread[thread.index(source_node):]
                       for thread in self.find_threads(source_node)]
        else:
            threads = self.threads
        m = max(len(thread) for thread in threads)
        for i in range(m):
            yield [thr[i] if len(thr) > i else None for thr in threads]


def get_tuple_index(l, index, value):
    for pos, t in enumerate(l):
        if t[index] == value:
            return pos
