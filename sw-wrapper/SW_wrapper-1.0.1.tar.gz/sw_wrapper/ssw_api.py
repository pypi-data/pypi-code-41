import ctypes as ct

from sw_wrapper import ssw_lib

def reverse_complement(seq):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    return "".join(complement.get(base, base) for base in reversed(seq))

def to_int(seq, lEle, dEle2Int):
    """
    translate a sequence into numbers
    @param  seq   a sequence
    """
    num_decl = len(seq) * ct.c_int8
    num = num_decl()
    for i, ele in enumerate(seq):
        try:
            n = dEle2Int[ele]
        except KeyError:
            n = dEle2Int[lEle[-1]]
        finally:
            num[i] = n

    return num


def align_one(ssw, qProfile, rNum, nRLen, nOpen, nExt, nFlag, nMaskLen):
    """
    align one pair of sequences
    @param  qProfile   query profile
    @param  rNum   number array for reference
    @param  nRLen   length of reference sequence
    @param  nFlag   alignment flag
    @param  nMaskLen   mask length
    """
    res = ssw.ssw_align(qProfile, rNum, ct.c_int32(nRLen), nOpen, nExt, nFlag, 0, 0, nMaskLen)

    nScore = res.contents.nScore
    nScore2 = res.contents.nScore2
    nRefBeg = res.contents.nRefBeg
    nRefEnd = res.contents.nRefEnd
    nQryBeg = res.contents.nQryBeg
    nQryEnd = res.contents.nQryEnd
    nRefEnd2 = res.contents.nRefEnd2
    lCigar = [res.contents.sCigar[idx] for idx in range(res.contents.nCigarLen)]
    nCigarLen = res.contents.nCigarLen
    ssw.align_destroy(res)

    return (nScore, nScore2, nRefBeg, nRefEnd, nQryBeg, nQryEnd, nRefEnd2, nCigarLen, lCigar)


def buildPath(q, r, nQryBeg, nRefBeg, lCigar):
    """
    build cigar string and align path based on cigar array returned by ssw_align
    @param  q   query sequence
    @param  r   reference sequence
    @param  nQryBeg   begin position of query sequence
    @param  nRefBeg   begin position of reference sequence
    @param  lCigar   cigar array
    """
    sCigarInfo = 'MIDNSHP=X'
    sCigar = ''
    sQ = ''
    sA = ''
    sR = ''
    nQOff = nQryBeg
    nROff = nRefBeg
    for x in lCigar:
        n = x >> 4
        m = x & 15
        if m > 8:
            c = 'M'
        else:
            c = sCigarInfo[m]
        sCigar += str(n) + c

        if c == 'M':
            sQ += q[nQOff: nQOff + n]
            sA += ''.join(['|' if q[nQOff + j] == r[nROff + j] else '*' for j in range(n)])
            sR += r[nROff: nROff + n]
            nQOff += n
            nROff += n
        elif c == 'I':
            sQ += q[nQOff: nQOff + n]
            sA += ' ' * n
            sR += '-' * n
            nQOff += n
        elif c == 'D':
            sQ += '-' * n
            sA += ' ' * n
            sR += r[nROff: nROff + n]
            nROff += n

    return sCigar, sQ, sA, sR


def align(sLibPath, query, target, bPath, bBest, nMatch, nMismatch, nOpen, nExt):
    lEle = []
    dRc = {}
    dEle2Int = {}
    dInt2Ele = {}
    # init DNA score matrix
    lEle = ['A', 'C', 'G', 'T', 'N']
    dRc = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'a': 'C', 'c': 'G', 'g': 'C', 't': 'A'}
    for i, ele in enumerate(lEle):
        dEle2Int[ele] = i
        dEle2Int[ele.lower()] = i
        dInt2Ele[i] = ele
    nEleNum = len(lEle)
    lScore = [0 for i in range(nEleNum ** 2)]
    for i in range(nEleNum - 1):
        for j in range(nEleNum - 1):
            if lEle[i] == lEle[j]:
                lScore[i * nEleNum + j] = nMatch
            else:
                lScore[i * nEleNum + j] = -nMismatch

    # translate score matrix to ctypes
    mat = (len(lScore) * ct.c_int8)()
    mat[:] = lScore
    # set flag
    nFlag = 0
    if bPath:
        nFlag = 2

    ssw = ssw_lib.CSsw(sLibPath)
    # iterate query sequence

        # build query profile
    qNum = to_int(query, lEle, dEle2Int)
    qProfile = ssw.ssw_init(qNum, ct.c_int32(len(query)), mat, len(lEle), 2)
        # build rc query profile
    if bBest:
        sQRcSeq = reverse_complement(query)#''.join([dRc[x] for x in query[::-1]])
        qRcNum = to_int(sQRcSeq, lEle, dEle2Int)
        qRcProfile = ssw.ssw_init(qRcNum, ct.c_int32(len(query)), mat, len(lEle), 2)
        # set mask len
    if len(query) > 30:
        nMaskLen = len(query) / 2
    else:
        nMaskLen = 15

        # iter target sequence
    rNum = to_int(target, lEle, dEle2Int)

            # format ofres: (nScore, nScore2, nRefBeg, nRefEnd, nQryBeg, nQryEnd, nRefEnd2, nCigarLen, lCigar)
    res = align_one(ssw, qProfile, rNum, len(target), nOpen, nExt, nFlag, nMaskLen)
            # align rc query
    resRc = None
    if bBest:
        resRc = align_one(ssw, qRcProfile, rNum, len(target), nOpen, nExt, nFlag, nMaskLen)

            # build cigar and trace back path
    strand = 0
    if resRc == None or res[0] > resRc[0]:
        resPrint = res
        strand = 0
        #sCigar, sQ, sA, sR = buildPath(query, target, res[4], res[2], res[8])
    else:
        resPrint = resRc
        strand = 1
        #sCigar, sQ, sA, sR = buildPath(sQRcSeq, target, resRc[4], resRc[2], resRc[8])

    ssw.init_destroy(qProfile)
    if bBest:
        ssw.init_destroy(qRcProfile)

            # print results
    if resPrint[2] + 1:
        target_begin = resPrint[2] + 1
    else:
        target_begin = 0
    target_end = resPrint[3] + 1
    if resPrint[4] + 1:
        query_begin = resPrint[4] + 1
    else:
        query_begin = 0
    query_end = resPrint[5] + 1
    optimal_score = resPrint[0]

    return optimal_score, strand, target_begin, target_end, query_begin, query_end
