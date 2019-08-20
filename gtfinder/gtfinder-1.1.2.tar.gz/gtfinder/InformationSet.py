from .Node import Node

class InformationSet:
    '''
    This class represents an informtion set
    '''
    def __init__(self, nodes):
        # usual checks
        assert isinstance(nodes, list)
        assert len(nodes) >= 1
        assert isinstance(nodes[0], Node)

        player = nodes[0].player
        actions = nodes[0].get_actions()
        for node in nodes:
            # checks all are nodes
            assert isinstance(node, Node)
            # checks actions are the sme and players are the same
            assert node.player == player
            assert sorted(node.get_actions()) == sorted(actions)
        self.player = player
        self.nodes = nodes
        self.actions = actions

    def __repr__(self):
        '''
        To be improved
        :return:
        '''
        return 'Information sets with player ' + self.player + '\n' + str(self.nodes)
