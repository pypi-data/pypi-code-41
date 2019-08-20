"""
this script is the basis to analyze a dynamic game
"""

import itertools
import numpy as np
from collections import defaultdict
from scipy.optimize import linprog
from Node import Node
from InformationSet import InformationSet


class ExtensiveFormGame:
    '''
    This class represent a dynamic game
    attributes after initialization:
    - players: list, contains the name of the players
    - root: Node, root node of the game
    - nodes: list, list of nodes in the game
    - L: list, contains all the information sets

    methods:
    - add_node: adds a terminal or partial history
    - get_nodes: print list of nodes in the game
    - get_paths: returns the list of possible plays of the game
    - create_information_set: creates an information set
    - get_strategies: this function creates a dictionary of the strategies
    - get_info_set_by_player: creates the list of information sets where the player is active
    - get_payoffs: returns the payoff resulting from a strategy profile
    - check_behavior_equivalent: check if two startegies are behaviourally equivalent
    - get_paths_from_strategy: returns all possible plays given a certain strategy
    - get_reduced_strategies_by_player: get the reduced strategies of a player
    - get_common_actions: get the actions in common between a list of strategies
    '''
    def __init__(self, players, first_player=None):
        '''
        To initialize you need to specify the name of the two players and the the first player to act
        :param players: list of players
        :param first_player: first player to act, defaul None that selects the first player in the players' list
        '''
        # save the list of players
        self.players = players
        # selects the first player of the list if first_player is not specified
        if first_player is None:
            first_player = players[0]

        # creates the root of the game
        self.root = Node(player=first_player)
        # creates a list of nodes, initializes it with the root
        self.nodes = [self.root]
        # creates an empty list it will contain the information sets
        self.L = []

    def __repr__(self):
        '''
        Repr, to be improved
        :return:
        '''
        return 'Extensive game tree ' + str(self.nodes)

    def add_node(self, parent, action, node):
        '''
        This function is used in two situations:
         - if node is a list, it adds a terminal history
         - if node is a node adds another node

        :param parent: Node, it is the node from which the action strts
        :param action: str, action from which it depends
        :param node: list or Node, resulting partial or terminal history
        '''
        # checks that parent is a node
        if not isinstance(parent, Node):
            raise(Exception('parent needs to be a valid node'))
        # checks that parents is a node of the game
        if not parent in self.nodes:
            raise (Exception('parent needs to be a node of the game'))
        # checks that node is either a list or a Node
        if not isinstance(node, Node) and not isinstance(node, list):
            raise (Exception('node needs to be a node or a list'))
        # use the add_child method of Node to add the child node
        parent.add_child(action, node)
        # if node is a partial history adds it to the list of nodes
        if isinstance(node, Node):
            self.nodes.append(node)

    def get_nodes(self):
        '''
        Print list of nodes in the game
        :return:
        '''
        for node in self.nodes:
            print(node)

    def get_paths(self):
        '''
        list of possible plays of the game
        :return:
        '''

        return self.root.get_paths()

    def create_information_set(self, nodes):
        '''
        This function creates an information set
        :param nodes:
        :return:
        '''

        self.L.append(InformationSet(nodes))

    def get_strategies(self):
        '''
        This function returns a dictionary containing as keys the players and as values their strategies
        :return:
        '''
        # initialize the dictionary
        strategies = {}
        # loop through all the players and through all the information set and creates the strategies for all players
        for player in self.players:
            actions = []
            sets = self.get_info_set_by_player(player)
            for set in sets:
                actions.append(set.actions)
            strategies[player] = list(itertools.product(*actions))
        return strategies

    def get_info_set_by_player(self, player):
        '''
        This function returns the information sets wehre the player is active
        :param player: str, name of the player
        :return: list, contains the information sets
        '''
        sets = []
        for info in self.L:
            if player == info.player:
                sets.append(info)
        return sets

    def get_payoffs(self, strategies):
        '''
        returns the payoff resulting from a strategy profile
        :param strategies: list, strategy profile
        :return: list, payoffs
        '''
        node = self.root
        player = self.root.player
        while True:
            strategy = strategies[player]
            node = node.go_down(strategy)
            if isinstance(node, list):
                return node
            player = node.player

    def check_behavior_equivalent(self, strategy_1, strategy_2, player):
        '''
        check if two startegies are behaviourally equivalent
        :param strategy_1:
        :param strategy_2:
        :param player:
        :return:
        '''
        paths_1 = self.get_paths_from_strategy(strategy_1, player)
        paths_2 = self.get_paths_from_strategy(strategy_2, player)
        if paths_1 == paths_2:
            return True
        else:
            return False

    def get_paths_from_strategy(self, strategy, player):
        '''
        returns all possible plays given a certain strategy
        :param strategy:
        :param player:
        :return:
        '''
        strategies = self.get_strategies()
        del strategies[player]
        combinations = [dict(zip(strategies.keys(), combination)) for combination in
                        itertools.product(*strategies.values())]
        paths = []
        for combination in combinations:
            path = ''
            combination[player] = strategy
            node = self.root
            active = self.root.player
            while True:
                strat = combination[active]
                node, action = node.go_down(strat, actions=True)
                path += action
                if isinstance(node, list):
                    break
                active = node.player
                path += ','
            paths.append(path)

        return sorted(paths)

    def get_reduced_strategies_by_player(self, player):
        '''
        get the reduced strategies of a player
        :param player:
        :return:
        '''
        strategies = self.get_strategies()
        player_strategies = strategies[player]
        del strategies[player]
        matrix = np.zeros((len(player_strategies), len(player_strategies)))
        for i in range(len(player_strategies)):
            for j in range(i, len(player_strategies)):
                if self.check_behavior_equivalent(player_strategies[i], player_strategies[j], player):
                    matrix[i, j] = 1
        # copia la parte sopra della matrice in quella sotto
        for i in range(matrix.shape[0]):
            for j in range(i, matrix.shape[1]):
                matrix[j][i] = matrix[i][j]
        RS = []
        uni = np.where(matrix == 1)
        equal = defaultdict(list)
        for i in range(len(uni[0])):
            equal[uni[0][i]].append(uni[1][i])
        for i in equal:
            equal[i] = sorted(equal[i])
        equal = list(equal.values())
        unique = [list(x) for x in set(tuple(x) for x in equal)]
        for u in unique:
            s = [player_strategies[i] for i in u]
            RS.append(self.get_common_actions(s))
        return RS

    def get_common_actions(self, strategies):
        '''
        get the actions in common between a list of strategies
        :param strategies:
        :return:
        '''
        new = []
        for action in strategies[0]:
            flag = True
            for strategy in strategies[1:]:
                if action not in strategy:
                    flag = False
            if flag:
                new.append(action)
        return new

    def get_strategies_by_info_set(self, info_set, reduced_strategies, player):
        '''
        This function finds the reduced strategies consistent with the information set
        :param info_set: InformationSet, information set we need to find the consisent strategies
        :return:
        '''
        players_strat = []
        if player == info_set.player:
            for strategy in reduced_strategies:
                if any(i in info_set.actions for i in strategy):
                    players_strat.append(strategy)

        else:
            for strat in reduced_strategies:
                paths = self.get_paths_from_strategy(strat, player)
                flag = False
                for path in paths:
                    if any(i in info_set.actions for i in path):
                        flag = True
                if flag:
                    players_strat.append(strat)

        return players_strat

    def initialization_step(self):
        # find the reduced strategies of the two players
        reduced_strat = {}
        for player in self.players:
            reduced_strat[player] = self.get_reduced_strategies_by_player(player)

        # this creates the functions of consistent reduced strategies
        functions_consistent_strategies = [{}, {}]
        for J in self.L:
            for i in range(len(self.players)):
                player = self.players[i]
                functions_consistent_strategies[i][J] = self.get_strategies_by_info_set(J, reduced_strat[player], player)

        # this creates the matrices
        M = []
        rows_and_columns = []
        for i in range(len(self.players)):
            player = self.players[i]
            info_sets = self.get_info_set_by_player(player)
            for J in info_sets:
                MJ = np.zeros((len(functions_consistent_strategies[i][J]), len(functions_consistent_strategies[(i+1)%2][J])))
                for k in range(len(functions_consistent_strategies[i][J])):
                    for j in range(len(functions_consistent_strategies[(i+1)%2][J])):
                        MJ[k][j] = self.get_payoffs({player: functions_consistent_strategies[i][J][k],
                                                     self.players[(i+1)%2]:functions_consistent_strategies[(i+1)%2][J][j]})[i]
                M.append(MJ)
                rows_and_columns.append([functions_consistent_strategies[i][J], functions_consistent_strategies[(i+1)%2][J]])

        return M, rows_and_columns

    def get_rationalizable_strategies(self):
        # list of matrices and of the lists of names of rows and columns
        M, rows_and_columns = self.initialization_step()
        # list of dominated strategies
        dominated = []

        while True:
            flag = []
            #loop thrugh all the matrices
            for i in range(len(M)):
                # select matrix, list of rows and columns and list of dominated rows
                MJ = M[i]
                row_and_col = rows_and_columns[i]
                dom = self.ro(MJ, row_and_col, dominated)
                for i in dom:
                    if i not in dominated:
                        flag.append(i)

            if len(flag) == 0:
                break
            else:
                for i in flag:
                    if i not in dominated:
                        dominated.append(i)

        reduced_strat = {}
        for player in self.players:
            reduced_strat[player] = self.get_reduced_strategies_by_player(player)
        for player in self.players:
            reduced_strat[player] = [i for i in reduced_strat[player] if i not in dominated]

        return reduced_strat


    def ro(self, MJ, row_and_col, dominated=[], verbose=False):
        '''
        rationalizable operator

        :param dominated: list of lists of dominated strategies, one for each player
        :return: updated list of dominated strategies
        '''
        new_dominated = [i.copy() for i in dominated]
        # create a list of lists of not dominated strategies
        rows = [row_and_col[0].index(i) for i in row_and_col[0] if i in dominated]
        columns = [row_and_col[1].index(i) for i in row_and_col[1] if i in dominated]

        not_dominated_rows = [i for i in range(MJ.shape[0]) if i not in rows]

        if verbose:
            print('the dominated is', new_dominated)
            print('dominated rows', rows)
            print('dominated columns', columns)

        # loop through all the not dominated rows and see if now are dominated
        for row in row_and_col[0]:
            if row_and_col[0].index(row) not in rows:
                if self.dominated(MJ, row_and_col[0].index(row), rows=rows, columns=columns):
                    new_dominated.append(row)

        return new_dominated

    def dominated(self, MJ, d_r, rows=[], columns=[]):
        '''
        This function checks if a strategy is strictly dominated

        :param MJ: matrice to start with
        :param d_r: strategy to check if dominated
        :param rows: already dominated strategies of player
        :param columns: already dominated strategies of other players
        :return: True if dominated False otherwise
        '''
        # Simple and fast check to be sure that the strategy is not already
        # among the one that are in the one that are not to take in consideration
        if d_r in rows:
            raise (Exception('trying to check an already dominated strategy'))

        if MJ.shape[0] - len(rows) <= 1:
            return False

        if MJ.shape[1] - len(columns) == 0:
            return False

        # matrix of the payoffs of the not dominated strategies different from d_r (hence the strategies that we are interested in)
        rationalizable_rows = [i for i in range(MJ.shape[0]) if i not in rows and i != d_r]
        rationalizable_columns = [i for i in range(MJ.shape[1]) if i not in columns]

        # copy the matrix selecting only the appropriate rows and columns
        payoffs = MJ[np.ix_(rationalizable_rows, rationalizable_columns)].T.copy()
        # create the objective function and the values of the constraints
        c = [1 for i in range(payoffs.shape[1])]
        b = MJ[np.ix_([d_r], rationalizable_columns)].copy()

        # if there are negative payoffs simply add them to all the others so that there are no negative ones
        if np.min(MJ) < 0:
            payoffs -= np.min(MJ)
            b -= np.min(MJ)

        # invert the verse of the constraint
        payoffs *= -1
        b *= -1
        # solve the LP problem

        res = linprog(c, A_ub=payoffs, b_ub=b, method='revised simplex', options={"presolve": False})

        # the strategy is strictly dominate only if there is a solution with value less then one and is feasible
        if res.fun < 1 and res.status == 0:
            return True
        else:
            return False

