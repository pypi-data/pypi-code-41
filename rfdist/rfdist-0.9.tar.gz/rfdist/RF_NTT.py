import time
import numpy as np
from numpy import transpose as t
from numpy import sum
from math import factorial
import math
#import primes
import ntt

Len=[8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072]
Primes=[113,115792089237316195423570985008687907853269984665640564039457584007913129637873,
         115792089237316195423570985008687907853269984665640564039457584007913129636801,
         115792089237316195423570985008687907853269984665640564039457584007913129636801,
         115792089237316195423570985008687907853269984665640564039457584007913129635457,
         115792089237316195423570985008687907853269984665640564039457584007913129607681,
         115792089237316195423570985008687907853269984665640564039457584007913129607681,
         1606938044258990275541962092341162602522202993782792835297281,
         115792089237316195423570985008687907853269984665640564039457584007913129461761,
         115792089237316195423570985008687907853269984665640564039457584007913129172993,
         115792089237316195423570985008687907853269984665640564039457584007913129172993,
         115792089237316195423570985008687907853269984665640564039457584007913126920193,
         2037035976334486086268445688409378161051468393665936250636140449354381299763336706178908161,
         2037035976334486086268445688409378161051468393665936250636140449354381299763336706177892353,
         2135987035920910082395021706169552114602704522356652769947041607822219725780640550022962063736833]
G=[3,21,21,7,14,14,17,3,5,5,5,7,3,3,5]
W=[18,111631467676984398667335374000770145103933448276474029826861642673272833963082,
    61564226408844285440839285786349609218130544814944526994086477601177658749278,
    81935540147743287569595753552990576696362777472267730857667504939936024849618,
    91170141105073899547981930648308993603853306285937430424976477296731306054334,
    15708606027314919182172787703297741273850535825986009804848210667018260880261,
    33237221508024116229589036146826233600929365121793224404567006713723969953911,
    1434356156435145496244722803431900791032286202821828147418984,
    63540838781496461220816358160078141041184179050497342724817951168620586697763,
    15509384003381570599629987132205606235150174359826996727314588125855310328659,
    25133251670451185231426344419964958947927332720991278511886330943333482712954,
    48268024184090406204552669607243172351613601631957894966972042240077595762455,
    1981954346943524807557239944865006706282615432034635354549839215713305664395133015635456087,
    255453916006749145705554152189433435708896877084778108205342427278941085195694645573514698,
    1112225229508435524512344497914210498809987905889897633818900952286269329043189880863555612895717]
Inv_W=[44,95491701939787783842804801121993865397654678743734107460462393771310698665647,
      14352436843288370756829869005573506932522362276688548257485320352002835319209,
        62892232488306180704111955726624356283223010632387729863360038676442428890163,
        74617868801387775053539490766464698026550495075777446366514898818780219762498,
        13868795121166213445530776440016103808108592816062879198885163286366532864581,
        110859567440002879494961048339626890678895648700881402044340171696425633801612,
        1203745758939828332217036953616990186340140894893888367743845,
        90289433802154956706057573109440369585442036636363262555556580120598543329883,
        21861149690056766619999951991678670952283712223678074390943578332757181356925,
        49072410160240151341757778422903690290128844704330943680519698627182085130938,
        20156023685761413501013067524878709675678100528950462782526586000840609710652,
        876083208576290984072439742436788642271124879220068514346599382871681217068777930632586646,
        1474657800099070887974174855844346785758665342966052193836639675246968569796074002531960855,
        1525680669204487905316664361660865987506438064471172450598417789819020549260814728309162207838676]

Inv_L=[99,108555083659983933209597798445644913612440610624038028786991485007418559035506,
        112173586448650064316584391727166410732855297644839296413224534507665844335651,
        113982837842983129870077688367927159293062641155239930226341059257789486986226,
        114887463540149662646824336688307533573166312910440247132899321632851308310180,
        115339776388732929035197660848497720713218148788040405586178452820382218945151,
        115565932813024562229384322928592814283244066726840484812818018414147674276416,
        1605368768825143605351003144985360685918177404921676826669061,
        115735550131243287125024319488664134460763505180940544232797692609471765629016,
        115763819684279741274297652248676021157016744923290554136127638308692447256691,
        115777954460797968348934318628681964505143364794465559087792611158302788214842,
        115785021849057081886252651818684936179206674730053061563625097583107956441255,
        2036973810929934862938176265628359808446455836647086582171460391357269654826210139506966666,
        2037004893632210474603310977018868984748962115156511416403800420355825477294773422841921621,
        2135970739633099406506331558604044839577416110609503442457036518698624890730242443329312596558002]

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


def RF_NTT(tree, n):
    """
    Calculates Robinson-Foulds metric for an ETE tree.
    :param tree: An ETE tree.
    :param n: Number of tips on the tree rooted.
    :return: 3 dimensional matrix
    """

    ntip = n - 1
    N = 0
    hp=(n-4)*(n-2)*3
    L= 2**(math.ceil(math.log(hp,10)/math.log(2,10)))


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
            R[v][1:ntip - 1, 0] = sum(np.transpose(Rchild[0:(ntip - 2), ] * B[0:(ntip - 1)]).T, axis=1)
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

            R1 = Rchild1[0:(ntip - 1), 0:(ntip - 3)]
            R1aug = np.zeros(L)
            t = 0
            for i in range(R1.shape[1]):
                R1aug[t:(t + R1.shape[0])] = R1[:, i]
                t = t + (3 * R1.shape[0])

            R2 = Rchild2[0:(ntip - 1), 0:(ntip - 3)]
            R2aug = np.zeros(L)
            t = 0
            for i in range(R2.shape[1]):
                R2aug[t:(t + R2.shape[0])] = R2[:, i]
                t = t + (3 * R2.shape[0])
            R1aug = R1aug.tolist()
            R2aug = R2aug.tolist()

            ind = Len.index(L)
            p = Primes[ind]
            w = W[ind]
            inv_w = Inv_W[ind]
            inv_L = Inv_L[ind]

            R1aug = [int(x) for x in R1aug]
            R2aug = [int(x) for x in R2aug]

            #start = time.time()
            Ivec1 = ntt.transform_fast(R1aug, w, p)
            Ivec2 = ntt.transform_fast(R2aug, w, p)
            Ivec3 = [(x * y) % p for (x, y) in zip(Ivec1, Ivec2)]
            conv = ntt.inverse_transform(Ivec3, inv_w, inv_L, p)
            pad = math.ceil(len(R1aug) / (3 * R1.shape[0]))
            conv_pad = [0] * (pad * 3 * R1.shape[0] - len(R1aug))
            sum3 = np.array(conv + conv_pad)
            #sum3 = np.array(sum3)
            nrow = 3 * R1.shape[0]
            ncol = len(sum3) // nrow
            sum3 = np.transpose(np.reshape(sum3, (ncol, nrow)))[0:R1.shape[0], 0:R1.shape[1]][1:R1.shape[0], ]
            #sum3 = np.transpose(sum3)
            #sum3 = sum3[0:R1.shape[0], 0:R1.shape[1]]
            #sum3 = sum3[1:R1.shape[0], ]
            z = np.zeros((R1.shape[0] - 1, 1))
            sum3 = np.concatenate((z, sum3), axis=1)
            #sum3_tf = time.time()
            #sum3_dt = sum3_tf - sum3_t0

            R[v][1:(ntip - 1), 1:(ntip - 1)] = sum1 + sum2 + sum3
    return R


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

def RF_NTT_sum3_performance(tree, n):
    """
    Calculates Robinson-Foulds metric for an ETE tree and records time of the sum3 section.
    :param tree: An ETE tree.
    :param n: Number of tips on the tree rooted.
    :return: 3 dimensional matrix, sum3 performances in 1 dimensional array of seconds
    """
    sum3_dt_list = []
    ntip = n - 1
    N = 0
    hp = (n - 4) * (n - 2) * 3
    L = 2 ** (math.ceil(math.log(hp, 10) / math.log(2, 10)))

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
            R[v][1:ntip - 1, 0] = sum(np.transpose(Rchild[0:(ntip - 2), ] * B[0:(ntip - 1)]).T, axis=1)
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

            R1 = Rchild1[0:(ntip - 1), 0:(ntip - 3)]
            R1aug = np.zeros(L)
            t = 0
            for i in range(R1.shape[1]):
                R1aug[t:(t + R1.shape[0])] = R1[:, i]
                t = t + (3 * R1.shape[0])

            R2 = Rchild2[0:(ntip - 1), 0:(ntip - 3)]
            R2aug = np.zeros(L)
            t = 0
            for i in range(R2.shape[1]):
                R2aug[t:(t + R2.shape[0])] = R2[:, i]
                t = t + (3 * R2.shape[0])
            R1aug = R1aug.tolist()
            R2aug = R2aug.tolist()

            ind = Len.index(L)
            p = Primes[ind]
            w = W[ind]
            inv_w = Inv_W[ind]
            inv_L = Inv_L[ind]

            R1aug = [int(x) for x in R1aug]
            R2aug = [int(x) for x in R2aug]

            sum3_t0 = time.time()
            Ivec1 = ntt.transform_fast(R1aug, w, p)
            Ivec2 = ntt.transform_fast(R2aug, w, p)
            Ivec3 = [(x * y) % p for (x, y) in zip(Ivec1, Ivec2)]
            conv = ntt.inverse_transform(Ivec3, inv_w, inv_L, p)
            pad = math.ceil(len(R1aug) / (3 * R1.shape[0]))
            conv_pad = [0] * (pad * 3 * R1.shape[0] - len(R1aug))
            sum3 = np.array(conv + conv_pad)
            # sum3 = np.array(sum3)
            nrow = 3 * R1.shape[0]
            ncol = len(sum3) // nrow
            sum3 = np.transpose(np.reshape(sum3, (ncol, nrow)))[0:R1.shape[0], 0:R1.shape[1]][1:R1.shape[0], ]
            z = np.zeros((R1.shape[0] - 1, 1))
            sum3 = np.concatenate((z, sum3), axis=1)
            sum3_tf = time.time()
            sum3_dt = sum3_tf - sum3_t0
            sum3_dt_list.append(sum3_dt)
            R[v][1:(ntip - 1), 1:(ntip - 1)] = sum1 + sum2 + sum3
    return R, sum3_dt_list


def polynomial(tree, n):
    """

    :param tree: ETE tree
    :param n: Number of tips on the ETE tree rooted
    :return: 1 dimensional array
    """
    Coef = []
    R = RF_NTT(tree, n)
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
    R, sum3_dt_list = RF_NTT_sum3_performance(tree, n)
    for i in range(0, 2 * (n - 2), 2):
        Coef.append(qmT(R, n, n - 3 - (i // 2)))
    return Coef, sum(sum3_dt_list)