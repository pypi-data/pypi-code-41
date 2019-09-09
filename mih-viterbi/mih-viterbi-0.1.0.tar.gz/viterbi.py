# encoding: utf-8

import numpy as np

from operator import itemgetter


class Viterbi(object):


    def __init__(self, p_state_init    = None,
                       p_state_trans   = None,
                       p_state_observe = None):

        self.p_state_init    = p_state_init
        self.p_state_trans   = p_state_trans
        self.p_state_observe = p_state_observe
        self.start           = 'null'



    def fit(self, X):

        pass



    def candidates_best(self, candidates):

        # candidates.sort(lambda i: i[2])
        candidates = sorted(candidates, key=itemgetter(2))
        best = [candidates[0]]

        for i in candidates[1:]:
            if best[0][2] != i[2]:
                break
            best.append(i)

        return best



    def path_best(self, pathes):

        best = []

        for p in pathes[-1]:
            path = []
            path.append(p[1])
            path.append(p[0])

            s = p[0]
            for i in pathes[:-1][::-1]:
                for j in i:
                    # 1st match
                    if s == j[1]:
                        s = j[0]
                        path.append(s)
                        break

            path = path[:-1][::-1]
            best.append(path)

        return best



    def predict(self, X):

        best = []

        for x in X:
            pathes = []

            candidates = []
            for s, p in self.p_state_init.iteritems():
                score = -np.log(p * self.p_state_observe.get(s,{}).get(x[0],0))
                candidates.append((self.start, s, score))

            pathes.append(self.candidates_best(candidates))

            # next observe
            for i in x[1:]:
                candidates = []
                for p in pathes[-1]:
                    for s in self.p_state_init.keys():
                        score = -np.log(self.p_state_trans.get(p[1],{}).get(s,0) *\
                                          self.p_state_observe.get(s,{}).get(i,0)) + p[2]
                        candidates.append((p[1], s, score))
                pathes.append(self.candidates_best(candidates))

            # best pathes
            best.append(self.path_best(pathes))

        return best
