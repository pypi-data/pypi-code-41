import time
import numpy as np
from numpy import transpose as t
from numpy import sum
from math import factorial


def Beta(m):
    """
    Double factorial of odd numbers: a(m) = (2*m-1)!! = 1*3*5*...*(2*m-1)
    :param m: integer
    :return: Integer
    """
    if m <= 0:
        ans = 1
    else:
        ans = 1
        for i in range(1, m):
            ans *= 2 * i + 1
    return ans


def internaledges(tree):
    """
    The function for computing the number of internal edges for each internal node
    :param tree: An ETE tree
    :return: Array of the number of internal edges for each internal node.
    """
    label_nodes(tree)
    ntip = len(tree.get_leaves())
    intedges = [0] * (ntip - 1)
    edges = get_edges(tree)
    for i in range(2 * ntip - 1, ntip, -1):
        children = []
        for idx, edge in enumerate(edges):
            if str(i) in edge[0].name:
                children.append(idx)
        child1 = edges[children[0]][1]
        child2 = edges[children[1]][1]
        child1num = int(child1.name[1:])
        child2num = int(child2.name[1:])
        if child1num <= ntip and child2num <= ntip:
            intedges[i - ntip - 1] = 0
        elif child1num <= ntip < child2num:
            intedges[i - ntip - 1] = intedges[child2num - ntip - 1] + 1
        elif child2num <= ntip < child1num:
            intedges[i - ntip - 1] = intedges[child1num - ntip - 1] + 1
        else:
            intedges[i - ntip - 1] = intedges[child2num - ntip - 1] + intedges[child1num - ntip - 1] + 2
    return intedges


def get_edges(tree):
    """
    Get edges of the tree in the form of (node_start,node_end)
    :param tree: ETE tree
    :return: List of edges of a tree of a list of tuples (node_start,node_end)
    """
    edges = []
    for node in tree.traverse("postorder"):
        if not node.is_leaf():
            edges.append((node, node.children[0]))
            edges.append((node, node.children[1]))
    return edges


def label_nodes(tree):
    """
    Label the internal nodes in the tree.
    :param tree: an ETE tree.
    :return: None
    """
    i = len(tree.get_leaves()) + 1
    t = 1
    for node in tree.traverse("preorder"):
        if not node.is_leaf():
            node.name = "n" + str(i)
            i += 1
        else:
            node.name = "t" + str(t)
            t += 1


def internalchildren(tree, v):
    """
        This function computes the number of internal children of each node. v is the node.
        :param tree: An ETE tree
        :param v: Integer label of node
        :return: Number of internal children for the node, v
        """
    label_nodes(tree)
    ntip = len(tree.get_leaves())
    edges = get_edges(tree)
    children = []
    for idx, edge in enumerate(edges):
        if str(v) in edge[0].name:
            children.append(idx)
    child1 = edges[children[0]][1]
    child2 = edges[children[1]][1]
    child1num = int(child1.name[1:])
    child2num = int(child2.name[1:])
    if child1num > ntip and child2num > ntip:
        result = [2, child1num, child2num]
    elif child1num > ntip >= child2num:
        result = [1, child1num]
    elif child2num > ntip >= child1num:
        result = [1, child2num]
    else:
        result = [0]
    return result


def RF(tree, n):
    """
    Calculates Robinson-Foulds metric for an ETE tree.
    :param tree: An ETE tree.
    :param n: Number of tips on the tree rooted.
    :return: 3 dimensional matrix
    """

    ntip = n - 1
    N = 0
    for node in tree.traverse("preorder"):
        if not node.is_leaf():
            N += 1
    R = np.zeros((ntip - 1, ntip - 1, N))
    edges = internaledges(tree)
    B = [0] * (n - 1)
    for k in range(len(B)):
        B[k] = Beta(k + 1)
    for v in range(N - 1, -1, -1):
        intchild = internalchildren(tree, v + ntip + 1)
        intedges = edges[v]
        if intchild[0] == 0:
            R[v][0, 0] = 1
        elif intchild[0] == 1:
            Rchild = R[intchild[1] - ntip - 1]
            R[v][0][intedges] = 1
            R[v][1:ntip - 1, 0] = sum(t(Rchild[0:(ntip - 2), ] * B[0:(ntip - 1)]).T, axis=1)
            R[v][1:(ntip - 1), 1:(ntip - 1)] = Rchild[1:(ntip - 1), 0:(ntip - 2)]
        else:
            Rchild1 = R[intchild[1] - ntip - 1]
            Rchild2 = R[intchild[2] - ntip - 1]

            R[v][0, intedges] = 1
            R[v][2, 0] = sum(Rchild1[0,] * B[0:(ntip - 1)] * sum(Rchild2[0,] * B[0:(ntip - 1)]))
            for s in range(3, (ntip - 1), 1):
                R[v][s, 0] = sum(sum(Rchild1[0:(s - 1), ] * B[0:(ntip - 1)], axis=1) * sum(
                    np.flip(Rchild2, axis=0)[(len(Rchild2) - (s - 1)):len(Rchild2), ] * B[0:(ntip - 1)], axis=1))

            sum1 = np.zeros((ntip - 2, ntip - 2))
            sum1[0, 0:(ntip - 2)] = sum(Rchild1[0,] * B[0:(ntip - 1)]) * Rchild2[0, 0:(ntip - 2)]
            for s in range(2, ntip - 1):
                temp = sum((sum(Rchild1[0:(s), ] * B[0:(ntip - 1)], axis=1) * np.flip(Rchild2, axis=0)[
                                                                              len(Rchild2) - (s):len(Rchild2),
                                                                              0:(ntip - 2)].T).T, axis=0)
                sum1[s - 1, 0:(ntip - 2)] = temp

            sum2 = np.zeros((ntip - 2, ntip - 2))
            sum2[0, 0:(ntip - 2)] = sum(Rchild2[0,] * B[0:(ntip - 1)]) * Rchild1[0, 0:(ntip - 2)]
            for s in range(2, (ntip - 1)):
                temp = sum((sum(Rchild2[0:(s), ] * B[0:(ntip - 1)], axis=1) * np.flip(Rchild1, axis=0)[
                                                                              len(Rchild1) - (s):len(Rchild1),
                                                                              0:(ntip - 2)].T).T, axis=0)
                sum2[s - 1][0:(ntip - 2)] = temp

            sum3 = np.zeros((ntip - 2, ntip - 2))
            for s in range(0, (ntip - 2)):
                for k in range(1, (ntip - 2)):
                    total3 = 0
                    for s1 in range(-1, s + 1):
                        for k1 in range(-1, (k - 1)):
                            total3 += Rchild1[s1 + 1][k1 + 1] * Rchild2[s - s1][k - 2 - k1]
                        sum3[s, k] = total3
            R[v][1:(ntip - 1), 1:(ntip - 1)] = sum1 + sum2 + sum3
    return R


def RF_sum3_performance(tree, n):
    """
    Calculates Robinson-Foulds metric for an ETE tree and records time of the sum3 section.
    :param tree: An ETE tree.
    :param n: Number of tips on the tree rooted.
    :return: 3 dimensional matrix, sum3 performances in 1 dimensional array of seconds
    """
    sum3_dt_list = []
    ntip = n - 1
    N = 0
    for node in tree.traverse("preorder"):
        if not node.is_leaf():
            N += 1
    R = np.zeros((ntip - 1, ntip - 1, N))
    edges = internaledges(tree)
    B = [0] * (n - 1)
    for k in range(len(B)):
        B[k] = Beta(k + 1)
    for v in range(N - 1, -1, -1):
        intchild = internalchildren(tree, v + ntip + 1)
        intedges = edges[v]
        if intchild[0] == 0:
            R[v][0, 0] = 1
        elif intchild[0] == 1:
            Rchild = R[intchild[1] - ntip - 1]
            R[v][0][intedges] = 1
            R[v][1:ntip - 1, 0] = sum(t(Rchild[0:(ntip - 2), ] * B[0:(ntip - 1)]).T, axis=1)
            R[v][1:(ntip - 1), 1:(ntip - 1)] = Rchild[1:(ntip - 1), 0:(ntip - 2)]
        else:
            Rchild1 = R[intchild[1] - ntip - 1]
            Rchild2 = R[intchild[2] - ntip - 1]

            R[v][0, intedges] = 1
            R[v][2, 0] = sum(Rchild1[0,] * B[0:(ntip - 1)] * sum(Rchild2[0,] * B[0:(ntip - 1)]))
            for s in range(3, (ntip - 1), 1):
                R[v][s, 0] = sum(sum(Rchild1[0:(s - 1), ] * B[0:(ntip - 1)], axis=1) * sum(
                    np.flip(Rchild2, axis=0)[(len(Rchild2) - (s - 1)):len(Rchild2), ] * B[0:(ntip - 1)], axis=1))

            sum1 = np.zeros((ntip - 2, ntip - 2))
            sum1[0, 0:(ntip - 2)] = sum(Rchild1[0,] * B[0:(ntip - 1)]) * Rchild2[0, 0:(ntip - 2)]
            for s in range(2, ntip - 1):
                temp = sum((sum(Rchild1[0:(s), ] * B[0:(ntip - 1)], axis=1) * np.flip(Rchild2, axis=0)[
                                                                              len(Rchild2) - (s):len(Rchild2),
                                                                              0:(ntip - 2)].T).T, axis=0)
                sum1[s - 1, 0:(ntip - 2)] = temp

            sum2 = np.zeros((ntip - 2, ntip - 2))
            sum2[0, 0:(ntip - 2)] = sum(Rchild2[0,] * B[0:(ntip - 1)]) * Rchild1[0, 0:(ntip - 2)]
            for s in range(2, (ntip - 1)):
                temp = sum((sum(Rchild2[0:(s), ] * B[0:(ntip - 1)], axis=1) * np.flip(Rchild1, axis=0)[
                                                                              len(Rchild1) - (s):len(Rchild1),
                                                                              0:(ntip - 2)].T).T, axis=0)
                sum2[s - 1][0:(ntip - 2)] = temp

            sum3_t0 = time.time()
            sum3 = np.zeros((ntip - 2, ntip - 2))
            for s in range(0, (ntip - 2)):
                for k in range(1, (ntip - 2)):
                    total3 = 0
                    for s1 in range(-1, s + 1):
                        for k1 in range(-1, (k - 1)):
                            total3 += Rchild1[s1 + 1][k1 + 1] * Rchild2[s - s1][k - 2 - k1]
                        sum3[s, k] = total3
            sum3_tf = time.time()
            sum3_dt = sum3_tf - sum3_t0
            sum3_dt_list.append(sum3_dt)
            R[v][1:(ntip - 1), 1:(ntip - 1)] = sum1 + sum2 + sum3
    return R, sum3_dt_list


def RsT(R, n, s):
    """

    :param R: 3 dimensional matrix
    :param n: integer
    :param s: integer
    :return: integer
    """
    B = []
    for k in range(0, (n - 2)):
        B.append(Beta(k + 1))
    # print(t(R[0][s,0:(n - 2 - s)]))
    rst = sum(t(t(R[0][s, 0:(n - 2 - s)]) * B[0:(n - 2 - s)]))
    return rst


def qmT(R, n, m):
    """

    :param R: 3 dimensional matrix
    :param n: integer
    :param m: integer
    :return: integer
    """
    qmt = 0
    for s in range(m, (n - 2)):
        rst = RsT(R, n, s)
        qmt = qmt + (factorial(s) / (factorial(m) * factorial(s - m))) * rst * pow((-1), (s - m))
    return qmt


def polynomial(tree, n):
    """

    :param tree: ETE tree
    :param n: Number of tips on the ETE tree rooted
    :return: 1 dimensional array
    """
    Coef = []
    R = RF(tree, n)
    for i in range(0, 2 * (n - 2), 2):
        Coef.append(qmT(R, n, n - 3 - (i // 2)))
    return Coef


def polynomial_sum3_performance(tree, n):
    """

    :param tree: ETE tree
    :param n: Number of tips on the ETE tree rooted
    :return: 1 dimensional array, sum3 performance in 1 dimensional array in seconds
    """
    Coef = []
    R, sum3_dt_list = RF_sum3_performance(tree, n)
    for i in range(0, 2 * (n - 2), 2):
        Coef.append(qmT(R, n, n - 3 - (i // 2)))
    return Coef, sum(sum3_dt_list)
