import numpy as np
import scipy.io
from scipy.stats import norm
from scipy.stats import truncnorm
from scipy.stats import t
from scipy.stats import invgamma
# import matplotlib.pyplot as plt
import copy

from .utility import *


class dts:
    def __init__(self, xdata, constraintIndicator, mus, sigmas, true_var, likelihood_setting, mTree):

        # table to represent tree
        # 0, node index 1, l. node index 2, r. node index
        # 3, cut dimension 4, cut value 5, cut level 6, mu val for termiinal node 7, variance for the standard deviation of ther terminal node
        self.constraintIndicator = constraintIndicator
        self.mus = mus
        self.sigmas = sigmas
        self.true_var = true_var
        self.treev = np.zeros([1, 7])
        self.var_a = 2
        self.var_b = 0.01
        self.mTree = mTree
        # self.treev[-1] = invgamma.rvs(a=self.var_a, loc=0, scale=self.var_b)
        if len(xdata.shape) == 1:
            self.treebound_lower = np.array([[np.min(xdata, axis=0)]])
            self.treebound_upper = np.array([[np.max(xdata, axis=0)]])
        else:
            self.treebound_lower = np.array([np.min(xdata, axis=0)])
            self.treebound_upper = np.array([np.max(xdata, axis=0)])

        self.nodeNumseq = [0]
        self.candidate_set = [[0]]
        self.likelihood_setting = likelihood_setting

        self.cut_prior = []
        self.cut_proposal = []




    def tree_full_gen(self, maxStage, alphav, betav, dimNum, xdata, ydata, add_dts_other_val):

        for tt in np.arange(maxStage):
            self.propose_cut(add_dts_other_val, alphav, betav, dimNum, xdata, ydata)
            if not self.candidate_set[-1]:
                break



    def propose_cut(self, add_dts_other_val, alphav, betav, dimNum, xdata, ydata):

        cu_canset = copy.deepcopy(self.candidate_set[-1])
        spe_nodeNum = copy.deepcopy(self.nodeNumseq[-1])

        ll_prior = 0
        ll_proposal = 0

        # intra_node = cu_canset[np.random.choice(len(cu_canset))]
        intra_node = np.random.choice(cu_canset)
        if np.random.rand() < (alphav / ((1 + self.treev[intra_node, 5]) ** betav)):
            self.treev[intra_node, 3] = np.random.choice(dimNum)
            self.treev[intra_node, 4] = np.random.uniform(self.treebound_lower[intra_node, self.treev[intra_node, 3].astype(int)],self.treebound_upper[intra_node, self.treev[intra_node, 3].astype(int)])

            add_treev = np.zeros([2, 7])
            add_treev[0, 0] = spe_nodeNum + 1
            add_treev[1, 0] = spe_nodeNum + 2
            add_treev[0, 5] = self.treev[intra_node, 5] + 1
            add_treev[1, 5] = self.treev[intra_node, 5] + 1

            #
            # implements the constraint version or unconstraint version here
            #
            prior_mu = np.mean(ydata)/self.mTree
            prior_var = 0.5
            y_differ = ydata - add_dts_other_val

            current_lower = copy.copy(self.treebound_lower[intra_node])
            current_upper = copy.copy(self.treebound_upper[intra_node])
            current_upper[self.treev[intra_node, 3].astype(int)] = self.treev[intra_node, 4]
            indexx_0 = index_judge(current_lower, current_upper, xdata)
            y_differ_1 = y_differ[indexx_0]
            current_lower = copy.copy(self.treebound_lower[intra_node])
            current_upper = copy.copy(self.treebound_upper[intra_node])
            current_lower[self.treev[intra_node, 3].astype(int)] = self.treev[intra_node, 4]
            indexx_1 = index_judge(current_lower, current_upper, xdata)
            y_differ_2 = y_differ[indexx_1]

            pre_var = self.true_var/(self.mTree*4)

            posterior_var_1 = (prior_var ** (-1) + len(y_differ_1) / pre_var) ** (-1)
            posterior_mu_1 = posterior_var_1 * (prior_mu / prior_var + np.sum(y_differ_1) / pre_var)
            posterior_var_2 = (prior_var ** (-1) + len(y_differ_2) / pre_var) ** (-1)
            posterior_mu_2 = posterior_var_2 * (prior_mu / prior_var + np.sum(y_differ_2) / pre_var)


            if self.constraintIndicator:

                low_region, upp_region = self.identify_lower_and_upper(intra_node, dimNum, xdata)

                stand_low_region = (low_region-posterior_mu_1)/(np.pi/(np.pi-1)*(posterior_var_1**(0.5)))
                stand_upp_region = (upp_region-posterior_mu_1)/(np.pi/(np.pi-1)*(posterior_var_1**(0.5)))
                bb = truncnorm.rvs(stand_low_region, stand_upp_region)
                add_treev[0, 6] = bb*(np.pi/(np.pi-1)*(posterior_var_1**(0.5)))+posterior_mu_1

                stand_low_region = (add_treev[0, 6]-posterior_mu_2)/(np.pi/(np.pi-1)*(posterior_var_2**(0.5)))
                stand_upp_region = (upp_region-posterior_mu_2)/(np.pi/(np.pi-1)*(posterior_var_2**(0.5)))
                bb = truncnorm.rvs(stand_low_region, stand_upp_region)
                add_treev[1, 6] = bb*(np.pi/(np.pi-1)*(posterior_var_2**(0.5)))+posterior_mu_2

                # stand_low_region = (low_region-self.mus)/(np.pi/(np.pi-1)*self.sigmas)
                # stand_upp_region = (upp_region-self.mus)/(np.pi/(np.pi-1)*self.sigmas)
                # bb = truncnorm.rvs(stand_low_region, stand_upp_region, size = 2)
                # originbb = bb
                # add_treev[0, 6] = np.min(originbb)
                # add_treev[1, 6] = np.max(originbb)

            else:

                if self.likelihood_setting == 1:
                    add_treev[0, 6] = norm.rvs(0, (pre_var*self.mTree)**(0.5))
                    add_treev[1, 6] = norm.rvs(0, (pre_var*self.mTree)**(0.5))
                else:
                    add_treev[0, 6] = norm.rvs(posterior_mu_1, posterior_var_1**(0.5))
                    add_treev[1, 6] = norm.rvs(posterior_mu_2, posterior_var_2**(0.5))

                    ll_prior1 = norm.logpdf(add_treev[0, 6], loc=prior_mu, scale=prior_var**(0.5))
                    ll_prior2 = norm.logpdf(add_treev[1, 6], loc=prior_mu, scale=prior_var**(0.5))
                    ll_proposal1 = norm.logpdf(add_treev[0, 6], loc=posterior_mu_1, scale=posterior_var_1**(0.5))
                    ll_proposal2 = norm.logpdf(add_treev[1, 6], loc=posterior_mu_2, scale=posterior_var_2**(0.5))

                    ll_prior = ll_prior1+ll_prior2
                    ll_proposal = ll_proposal1+ll_proposal2

                # else:
                #     add_treev[0, 6] = t.rvs(df = 3, loc = self.mus, scale = self.sigmas)
                #     add_treev[1, 6] = t.rvs(df = 3, loc = self.mus, scale = self.sigmas)

            # add_treev[0, 7] = 0.01
            # add_treev[1, 7] = 0.01
            self.treev[intra_node, [1, 2]] = np.array([1, 2]) + spe_nodeNum


            self.treev = np.vstack((self.treev, add_treev))

            # set up the new lower & upper bound for the node of spe_nodeNum+1 and spe_nodeNum+2
            added_treebound_lower = np.tile(self.treebound_lower[intra_node], (2, 1))
            added_treebound_upper = np.tile(self.treebound_upper[intra_node], (2, 1))
            added_treebound_upper[0, self.treev[intra_node, 3].astype(int)] = self.treev[intra_node, 4]
            added_treebound_lower[1, self.treev[intra_node, 3].astype(int)] = self.treev[intra_node, 4]

            # np.concatenate((np.array([[treebound_lower]]), added_treebound_lower), axis=0)
            self.treebound_lower = np.vstack((self.treebound_lower, added_treebound_lower))
            self.treebound_upper = np.vstack((self.treebound_upper, added_treebound_upper))

            cu_canset.extend([1 + spe_nodeNum, 2 + spe_nodeNum])
            spe_nodeNum += 2
        cu_canset.remove(intra_node)

        self.nodeNumseq.append(spe_nodeNum)
        self.candidate_set.append(cu_canset)
        self.cut_prior.append(ll_prior)
        self.cut_proposal.append(ll_proposal)


    def checkMono(self):

        nonempty_index = np.where(self.treev[:, 2]!=0)
        valss = self.treev[nonempty_index, 1]
        case2 = (len(valss[0])>len(np.unique(valss[0])))

        return case2


    def identify_lower_and_upper(self, intra_node,dimNum, xdata):
        lowerss = self.treebound_lower[intra_node]
        upperss = self.treebound_upper[intra_node]
        terminal_nodes = self.treev[self.treev[:, 1]==0, 0]
        terminal_lower = self.treebound_lower[terminal_nodes.astype(int)]
        terminal_upper = self.treebound_upper[terminal_nodes.astype(int)]

        if dimNum == 1:
            below_neighbor_regions = terminal_nodes[lowerss==terminal_upper[:, 0]]
            above_neighbor_regions = terminal_nodes[upperss==terminal_lower[:, 0]]

            if not len(below_neighbor_regions):
                low_region = np.min(xdata)
            else:
                low_region = np.max(self.treev[below_neighbor_regions.astype(int), 6])
            if not len(above_neighbor_regions):
                upp_region = np.max(xdata)
            else:
                upp_region = np.min(self.treev[above_neighbor_regions.astype(int), 6])
        else:
            below_neighbor_regions = terminal_nodes[np.sum(lowerss==terminal_upper, axis = 1).astype(bool)]
            above_neighbor_regions = terminal_nodes[np.sum(upperss==terminal_lower, axis = 1).astype(bool)]

            if not len(below_neighbor_regions):
                low_region = np.min(xdata)
            else:
                low_region = np.max(self.treev[below_neighbor_regions.astype(int), 6])
            if not len(above_neighbor_regions):
                upp_region = np.max(xdata)
            else:
                upp_region = np.min(self.treev[above_neighbor_regions.astype(int), 6])

        return low_region, upp_region

    def assign_to_data(self, xdata, stage_i):
        terminal_node = self.dts_coor_belong(xdata, stage_i)
        mi_dts_val_data = self.treev[terminal_node, 6]
        return mi_dts_val_data

    def ll_cal(self, xdata, ydata, add_dts_other_val, stage_i):
        # we need to define the likelihood here for cutting the block
        mi_dts_val_data = self.assign_to_data(xdata, stage_i)
        predicted_yval = add_dts_other_val + mi_dts_val_data

        if self.likelihood_setting == 0: # normal random distribution
            return np.sum(norm.logpdf(ydata, predicted_yval, self.true_var**(0.5)))
        elif self.likelihood_setting == 1: # logistic regression
            return np.sum((ydata==0)*(-predicted_yval))-np.sum(np.log(1+np.exp(-predicted_yval)))


    def dts_coor_belong(self, coors, stage_i):
        aa = copy.deepcopy(self.treev[:(stage_i+1), 2])
        aa[aa>stage_i] = 0
        terminal_index = np.where(aa==0)[0]
        terminal_lower = self.treebound_lower[terminal_index]
        terminal_upper = self.treebound_upper[terminal_index]

        if len(coors.shape)==1:
            indicator_index = (coors.reshape((1, -1))>=terminal_lower)&((coors.reshape((1, -1))<=terminal_upper))
            nonempty_index = np.dot(indicator_index.T, np.arange(len(terminal_lower)))
        else:
            compare_mat_lower = ((coors[np.newaxis].swapaxes(1, 0) - terminal_lower[np.newaxis])>=0)
            compare_mat_upper = ((coors[np.newaxis].swapaxes(1, 0) - terminal_upper[np.newaxis])<=0)
            indicator_index = (np.prod(compare_mat_lower, axis=2))*(np.prod(compare_mat_upper, axis = 2))

            nonempty_index = np.dot(indicator_index, np.arange(len(terminal_lower)))
        terminal_node = terminal_index[nonempty_index]

        return terminal_node


    def dts_update(self, particleNUm, dts_star, maxStage, xdata, ydata, add_dts_other_val, alphav, betav, dimNum):
        par_dts_seq = []
        for pari in range(particleNUm):
            dts_pari = dts(xdata, self.constraintIndicator, self.mus, self.sigmas, self.true_var, self.likelihood_setting, self.mTree)
            # dts_pari.tree_full_gen(maxStage, alphav, betav, dimNum, xdata, ydata)
            par_dts_seq.append(dts_pari)

        previous_ll = np.zeros(particleNUm + 1)
        hd_i = 0
        continue_flag = True
        # for hd_i in np.arange(1, maxstage_PG, 1):
        while(continue_flag):
            hd_i += 1
            continue_flag = False
            ll_seqi = []
            for pari in range(particleNUm):
                # print(par_dts_seq[pari].candidate_set)

                # if (hd_i >= len(par_dts_seq[pari].candidate_set)) & (par_dts_seq[pari].candidate_set[-1]==[]):
                if (par_dts_seq[pari].candidate_set[-1]):
                    continue_flag = True
                    par_dts_seq[pari].propose_cut(add_dts_other_val, alphav, betav, dimNum, xdata, ydata)
                ll_val_i = (par_dts_seq[pari].ll_cal(xdata, ydata, add_dts_other_val, par_dts_seq[pari].nodeNumseq[-1]))
                ll_seqi.append(ll_val_i+par_dts_seq[pari].cut_prior[-1]-par_dts_seq[pari].cut_proposal[-1])

            if hd_i >= len(self.candidate_set):
                ll_seqi.append(self.ll_cal(xdata, ydata, add_dts_other_val, self.nodeNumseq[-1]))
            else:
                star_cut_prior = self.cut_prior[hd_i-1]
                star_cut_proposal = self.cut_proposal[hd_i-1]
                ll_seqi.append(self.ll_cal(xdata, ydata, add_dts_other_val, self.nodeNumseq[hd_i])+star_cut_prior-star_cut_proposal)

            # We might not use previous_ll
            # ll_seqi_ratio = ll_seqi-previous_ll
            ll_seqi_ratio = ll_seqi-previous_ll

            # normalize the log-likelihood
            propb = np.exp(ll_seqi_ratio-np.max(ll_seqi_ratio))

            copy_dts_star = copy.deepcopy(dts_star)
            par_dts_seq.append(tree_stage_cut(copy_dts_star, hd_i))

            if continue_flag:
                select_index = np.random.choice((particleNUm + 1), particleNUm, replace=True, p=propb / np.sum(propb))

                par_dts_seq[:particleNUm] = [copy.deepcopy(par_dts_seq[i]) for i in select_index]
                previous_ll[:particleNUm] = [copy.deepcopy(ll_seqi[i]) for i in select_index]
                previous_ll[-1] = copy.deepcopy(ll_seqi[-1])
                par_dts_seq.pop()

            else:
                select_index = np.random.choice((particleNUm + 1), replace=True, p=propb / np.sum(propb))
                final_particle = par_dts_seq[select_index]
                break



        self.treev = final_particle.treev
        self.treebound_lower = final_particle.treebound_lower
        self.treebound_upper = final_particle.treebound_upper
        self.nodeNumseq = final_particle.nodeNumseq
        self.candidate_set = final_particle.candidate_set

        self.cut_prior = final_particle.cut_prior
        self.cut_proposal = final_particle.cut_proposal





class add_dts:

    def __init__(self, mTree, constraintIndicator, mus, sigmas, maxStage, alphav, betav, dimNum, xdata, ydata,likelihood_setting):
        self.mTree = mTree
        self.true_var = sigmas**2

        add_dts = []
        add_dts_other_val = 0
        for mi in range(mTree):
            mi_dts = dts(xdata, constraintIndicator, mus, sigmas, self.true_var, likelihood_setting, mTree)
            mi_dts.tree_full_gen(maxStage, alphav, betav, dimNum, xdata, ydata, add_dts_other_val)
            add_dts.append(mi_dts)
            add_dts_other_val += mi_dts.assign_to_data(xdata, mi_dts.nodeNumseq[-1])
        self.add_dts = add_dts
        self.likelihood_setting = likelihood_setting

    # def update_mu(self, xdata, ydatas):
    #
    #     prior_mu = 0
    #     prior_var = 0.5
    #
    #     total_val_mat = np.zeros([self.mTree, len(xdata)])
    #     for mi in range(self.mTree):
    #         total_val_mat[mi] = self.add_dts[mi].assign_to_data(xdata, self.add_dts[mi].nodeNumseq[-1])
    #     sum_total_val_mat = np.sum(total_val_mat, axis=0)
    #
    #     for treei in range(self.mTree):
    #         mu_val_absent_treei = sum_total_val_mat-total_val_mat[treei]
    #         y_differ = ydatas - mu_val_absent_treei
    #
    #         unique_stage = np.unique(self.add_dts[treei].nodeNumseq)
    #         finished_set = []
    #         for ustage_index in range(len(unique_stage)):
    #             candidate_terminal = self.add_dts[treei].candidate_set[ustage_index]
    #             # print(candidate_terminal)
    #             candidate_terminal = list(set(candidate_terminal)-set(finished_set))
    #             # print(candidate_terminal)
    #             # print(finished_set)
    #             xdata_belong = self.add_dts[treei].dts_coor_belong(xdata, unique_stage[ustage_index])
    #             for ti in candidate_terminal:
    #                 finished_set.append(ti)
    #                 ti_y_differ = y_differ[xdata_belong==ti]
    #                 posterior_var = (prior_var**(-1)+len(ti_y_differ)/self.true_var)**(-1)
    #                 posterior_mean = posterior_var*(prior_mu/prior_var+np.sum(ti_y_differ)/self.true_var)
    #                 self.add_dts[treei].treev[ti, 6] = norm.rvs(loc=posterior_mean, scale=(posterior_var**(0.5)))


    def hyper_sigma_update(self, xdata, ydata):
        hyper_sigma_1 = 2
        hyper_sigma_2 = 0.25
        # update the hyper-parameters of the sigmas

        sigma_prior_choice = 1

        total_val_mat = np.zeros([self.mTree, len(xdata)])
        for mi in range(self.mTree):
            # total_val_mat[mi], total_var_mat[mi] = add_dts_v.add_dts[mi].assign_to_data(xdata, add_dts_v.add_dts[mi].nodeNumseq[-1])
            total_val_mat[mi] = self.add_dts[mi].assign_to_data(xdata, self.add_dts[mi].nodeNumseq[-1])

        if sigma_prior_choice == 1:  # set the inverse gamma distribution as the prior for variance

            posterior_hyper_sigma_1 = hyper_sigma_1 + len(xdata)/ 2  # the number refers to the number of terminal nodes
            square_of_errors = np.sum((np.sum(total_val_mat, axis=0)-ydata)**2)
            posterior_hyper_sigma_2 = hyper_sigma_2 + square_of_errors / 2
            self.true_var = invgamma.rvs(a = posterior_hyper_sigma_1, loc = 0, scale = posterior_hyper_sigma_2)
        elif sigma_prior_choice == 2: # use metropolis-hastings algorithm to update variance
            musval = np.sum(total_val_mat, axis = 0)
            new_true_var = invgamma.rvs(a=hyper_sigma_1, loc=0, scale=hyper_sigma_2)

            if self.likelihood_setting == 0:
                origin_ll = np.sum(norm.logpdf(ydata, musval, self.true_var ** (0.5)))
                new_ll = np.sum(norm.logpdf(ydata, musval, scale=new_true_var ** (0.5)))
            if np.log(np.random.rand())<(new_ll-origin_ll):
                self.true_var = new_true_var
        # elif sigma_prior_choice == 3: # set the inverse chi-square distribution as the prior for variance


    def updates(self, particleNUm, maxStage, xdata, ydata, alphav, betav, dimNum):
        total_val_mat = np.zeros([self.mTree, len(xdata)])
        for mi in range(self.mTree):
            total_val_mat[mi] = self.add_dts[mi].assign_to_data(xdata, self.add_dts[mi].nodeNumseq[-1])

        for mi in range(self.mTree):

            add_dts_other_val = np.sum(total_val_mat, axis = 0) - total_val_mat[mi]

            dts_mi = copy.deepcopy(self.add_dts[mi])
            dts_mi.dts_update(particleNUm, dts_mi, maxStage, xdata, ydata, add_dts_other_val, alphav, betav, dimNum)
            self.add_dts[mi] = dts_mi
            total_val_mat[mi] = dts_mi.assign_to_data(xdata, dts_mi.nodeNumseq[-1])

