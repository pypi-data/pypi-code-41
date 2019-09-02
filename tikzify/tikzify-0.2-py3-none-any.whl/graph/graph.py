import itertools as it
import keyword
from collections.abc import Mapping

import networkx as nx
import numpy as np

from .edge import Edge
from .multi_edge import create_waypoints
from .node import generate_node

__all__ = ['NodeGraph']


class NodeGraph:

    class GeneralAnchor:

        def as_tikz_ex(self):
            return self.as_tikz()

        @staticmethod
        def str_helper(s):
            try:
                return s.as_tikz()
            except AttributeError:
                return s

        @staticmethod
        def base_node_helper(l):
            for x in l:
                if isinstance(x, str):
                    yield x
                else:
                    yield from x.base_nodes()

    class Coordinate(GeneralAnchor):

        def __init__(self, x, y):
            self.x = x
            self.y = y

        def as_tikz(self):
            return "{}, {}".format(
                *(self.str_helper(x) for x in [self.x, self.y]))

        def as_array(self):
            return np.array([self.x, self.y], dtype='f')

        def base_nodes(self):
            return []

        def __repr__(self):
            return f'{type(self).__name__}({self.x:.4f}, {self.y:.4f})'

    class Midpoint(GeneralAnchor):

        def __init__(self, x, y, fraction=0.5):
            self.x = x
            self.y = y
            self.fraction = fraction

        def as_tikz(self):
            return "$({})!{}!({})$".format(self.str_helper(self.x),
                                           self.fraction,
                                           self.str_helper(self.y))

        def base_nodes(self):
            return self.base_node_helper([self.x, self.y])

    class Anchor(GeneralAnchor):

        def __init__(self, node, anchor):
            self.node = node
            self.anchor = str(anchor)

        def as_tikz(self):
            return "{}.{}".format(self.node, self.anchor)

        def base_nodes(self):
            return self.base_node_helper([self.node])

    class Node(GeneralAnchor):

        def __init__(self, node):
            self.node = node

        def as_tikz(self):
            return self.node

        def base_nodes(self):
            return self.base_node_helper([self.node])

    class Intersection(GeneralAnchor):

        def __init__(self, xnode, ynode):
            self.xnode = xnode
            self.ynode = ynode

        def as_tikz(self):
            return "{} |- {}".format(
                *(self.str_helper(x) for x in [self.xnode, self.ynode]))

        def base_nodes(self):
            return self.base_node_helper([self.xnode, self.ynode])

    def __init__(self,
                 nodes=None,
                 edges=None,
                 node_text=(lambda x: x),
                 node_type=(lambda x: set()),
                 edge_colors=None):
        """
        node_text and node_type are either
        * a callable that maps node names to *,
        * None in which case the map is the identity
        """
        self.edge_colors = ({}
                            if edge_colors is None
                            else edge_colors)
        self.digraph = nx.MultiDiGraph()
        if nodes:
            self.digraph.add_nodes_from(nodes)
        if edges:
            self.digraph.add_edges_from(edges)

        def lookup(y, node):
            """
            y is none or map or callable
            """
            if callable(y):
                return y(node)
            if isinstance(Mapping):
                return y[node]
            return y
        for node in self.digraph:
            node_dict = self.digraph.node[node]
            if 'text' not in node_dict:
                node_dict['text'] = lookup(node_text, node)
            if 'type' not in node_dict:
                node_dict['type'] = lookup(node_type, node)

    @property
    def nodes(self):
        return sorted(self.digraph)

    def __repr__(self):
        return repr(self.digraph)

    @staticmethod
    def math_name(name):
        """
        Given "A3", returns "$A_3$".
        """
        if len(name) == 2 and name[1] != "'":
            name = name[0] + '_' + name[1]
        return '${}$'.format(name)

    def toposorted(self):
        g = self.digraph
        g2 = nx.DiGraph()
        g2.add_nodes_from(g)
        for name in g:
            node_dict = g.node[name]
            if 'fit' in node_dict:
                for fit in node_dict['fit']:
                    g2.add_edge(fit, name)
            if 'pos' in node_dict:
                rel_node = node_dict['pos']
                if not isinstance(rel_node, self.GeneralAnchor):
                    raise TypeError
                for node in rel_node.base_nodes():
                    g2.add_edge(node, name)
            if 'relpos' in node_dict:
                _, _, rel_node = node_dict['relpos']
                if not isinstance(rel_node, self.GeneralAnchor):
                    raise TypeError
                for node in rel_node.base_nodes():
                    g2.add_edge(node, name)
        try:
            return list(nx.lexicographical_topological_sort(g2)), g2
        except nx.nx.NetworkXUnfeasible:
            print("Cycles", list(nx.simple_cycles(g2)))
            raise

    def fix_opacity(self):
        g = self.digraph
        toposorted, dependency_graph = self.toposorted()
        for name in toposorted:
            o = g.node[name].get('opacity', 0.0)
            for successor in it.chain([name],
                                      dependency_graph.successors(name)):
                for ed in it.chain(g.succ[successor].values(),
                                   g.pred[successor].values()):
                    for tip in ed.values():
                        o = max(o, tip.get('opacity', 1.0))
            if not g.node[name].get('dimming_restrictive', False):
                for fit in g.node[name].get('fit', []):
                    o = max(o, g.node[fit].get('opacity', 1.0))
            g.node[name]['opacity'] = o

    def generate(self, f):
        g = self.digraph
        toposorted, _ = self.toposorted()
        sorted_names = list(toposorted)

        for name in sorted_names:
            node_dict = g.node[name]
            if node_dict.get('draw', True):
                generate_node(name, node_dict, file=f)

        for source in sorted_names:
            for (target, ed) in sorted(g.succ[source].items()):
                len_ed = len(ed)
                for i, tip in enumerate(ed.values()):
                    tip = tip.copy()
                    # i_prime = (len_ed - i - 1) if bend_rev else i
                    if 'loop' not in tip:
                        bend = tip.get('bend', 0)
                        bend += (0
                                 if len_ed == 1 else
                                 (2 * i - 1) * 14
                                 if len_ed == 2 else
                                 (i - 1) * 20
                                 if len_ed == 3 else
                                 0)
                        tip['bend'] = bend

                    keywords_passed = set(keyword.kwlist) & set(tip)
                    if keywords_passed:
                        raise ValueError(
                            "Keyword passed as argument: {}".format(
                                keywords_passed.pop()))

                    via = tip.pop('via', None)
                    edge = Edge(**tip, edge_colors=self.edge_colors)
                    if via is not None:
                        vertical, turns, waypoint_names = via
                        create_waypoints(f,
                                         edge,
                                         source,
                                         list(turns) + [target],
                                         vertical,
                                         waypoint_names)
                    else:
                        edge.pf(f, source, target)
