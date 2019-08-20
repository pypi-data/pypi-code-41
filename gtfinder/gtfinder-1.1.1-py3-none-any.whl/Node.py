class Node:
    '''
    This class represent a single decision node

    attributes after init:
    - player: str, player active at this node
    - children: dict, as keys the actions and as values the children nodes
    - brothers: list, nodes in the same information set

    methods:
    - add_child: adds a terminal history or another child node
    - get_actions: return the list of actions
    - get_children: return the list of terminal and partial histories directly depending from the node
    - go_down: return the children that comes up with that strategy
    - get_paths: returns the posiible plays strating from the node
    '''
    def __init__(self, player='1'):
        self.player = player
        self.children = {}
        self.brothers = []

    def __repr__(self):
        '''
        To be improved
        :return:
        '''
        return 'Node with player ' + self.player + '\n' + str(self.get_actions())

    def add_child(self, action, node):
        '''
        This function is used in two situations:
         - if node is a list, it adds a terminal history
         - if node is a node adds another node

        :param action: str, action from which it depends
        :param node: list or Node, resulting partial or terminal history
        '''
        # checks that node is either a list or a Node
        if not isinstance(node, Node) and not isinstance(node, list):
            raise (Exception('node needs to be a node or a list'))
        # update the children dictionary
        self.children[action] = node

    def get_actions(self):
        '''
        returns the list of actions
        :return: list, list of actions
        '''
        return list(self.children.keys())

    def get_children(self):
        '''
        return the list of terminal and partial histories directly depending from the node
        :return: list, children of the node
        '''
        return list(self.children.values())

    def go_down(self, strategy, actions=False):
        '''
        return the children that comes up with that strategy
        :param strategy: list, strategy used
        :param actions: bool, if true returns the tuple (children, action)
        :return:
        '''
        for i in strategy:
            if i in self.get_actions():
                if actions:
                    return self.children[i], i
                return self.children[i]

    def get_paths(self):
        '''
        returns all the possible plays starting from this node, recursive approach
        :return:
        '''
        paths = []
        for action in self.get_actions():
            if isinstance(self.children[action], list):
                paths.append(action)
            else:
                paths.extend([action + ',' + i for i in self.children[action].get_paths()])
        return paths
