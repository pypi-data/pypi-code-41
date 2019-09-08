# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3


class CycleException(Exception):
    pass


def __min_priority(priorities, nodes):
    priority = "z"
    resultset = set()
    for node in nodes:
        if priorities[node] < priority:
            priority = priorities[node]
            resultset = set([node])
        elif priorities[node] == priority:
            resultset.add(node)

    return resultset


# Topographical sorting based on Kahn's algorithm, with the smallest elements
# appearing early to ensure consisteny between runs
# Graph is a dictionary mapping each vertex to a set containing its children.
# Priority is a dictionary mapping each vertex to a priority in [0-9z]
def tsort(graph, priority=None):
    _graph = graph.copy()
    L = []
    S = set([node for node in _graph.keys()])

    for edges in _graph.values():
        S -= edges

    while len(S) > 0:
        # We always take the smallest value from the set, rather than an arbitrary value
        if priority is None:
            smallest = min(S)
        else:
            smallest = min(__min_priority(priority, S))

        S.remove(smallest)
        L.append(smallest)

        s_set = _graph[smallest]
        _graph[smallest] = set()
        for node in s_set:
            if not any([node in edges for edges in _graph.values()]):
                S.add(node)

    if any([len(edges) > 0 for edges in _graph.values()]):
        # Graph has at least one cycle
        raise Exception("There is a cycle in the graph!")

    return L
