from .one import WANNNode


class WANN:
    def __init__(self, parameters_len, targets_len, start_nodes):
        self.all_nodes = (
                [WANNNode(parents=set([start_node for start_node in start_nodes]))] +
                [WANNNode(node_value=0) for _ in range(parameters_len)]
        )
        self.parameters_len = parameter_len
        self.targets_len = targets_len
        for i in range(target_len):
            self.all_nodes[start_nodes[i]].add_child(i)

    def add_node(self, parent_node, child_node):
        self.all_nodes.append(WANNNode(parents=[parent_node], children=[child_node]))
        new_node = len(self.all_nodes) - 1

        self.all_nodes[parent_node].add_child(new_node)
        self.all_nodes[parent_node].delete_children(child_node)

        self.all_nodes[child_node].add_parent(new_node)
        self.all_nodes[child_node].delete_parent(parent_node)

    def add_connection(self, parent_node, child_node):
        self.all_nodes[parent_node].add_child(child_node)
        self.all_nodes[child_node].add_parent(parent_node)

    def change_activation(self, node, activation):
        self.all_nodes[node].change_activation(activation)

    def result(self, weight, parameters):
        for i in range(self.targets_len, self.parameters_len + self.targets_len):
            self.all_nodes[i].node_value = parameters[i - self.targets_len]

        result = []
        for i in range(len(self.target)):
            result.append(self.all_nodes[i].calculate(weight, self.all_nodes))

        return result

    def clone(self):
        new_net = WANN(
            parameters_len=self.parameters_len,
            targets_len=self.targets_len,
            start_nodes=[]
        )
        new_net.all_nodes = [self.all_nodes[i].clone() for i in range(len(self.all_nodes))]
        return new_net
