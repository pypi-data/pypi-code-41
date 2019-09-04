import numpy as np


class WANNNode:
    def __init__(self, parents=set(), children=set(), activation=linear, node_value=None):
        self.parents = set(parents)
        self.children = set(children)
        self.activation = activation
        # for input nodes
        self.node_value = node_value

    def add_parent(self, parent_node):
        self.parents.add(parent_node)

    def delete_parent(self, parent_node):
        self.parents.remove(parent_node)

    def add_child(self, child_node):
        self.children.add(child_node)

    def delete_child(self, child_node):
        self.children.remove(child_node)

    def change_activation(self, activation):
        self.activation = activation

    def set_of_parents(self, all_nodes):
        parents = set()
        parents.update(self.parents)
        for parent in self.parents:
            parents.update(all_nodes[parent].set_of_parents(all_nodes))
        return parents

    def calculate(self, weight, all_nodes):
        if len(self.parents):
            result = np.sum(
                [all_nodes[ind].calculate(weight, all_nodes) for ind in parents]) * weight
        else:
            result = self.node_value
        return self.activation(result)

    def clone(self):
        new_node = WANNNode(parents=self.parents, children=self.children,
                            activation=self.activation, node_value=self.node_value)
        return new_node
