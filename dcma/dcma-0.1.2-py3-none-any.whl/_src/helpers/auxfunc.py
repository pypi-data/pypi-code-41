from pathlib import Path
from Bio.SeqIO import FastaIO
from anytree import AnyNode, LevelOrderGroupIter
from itertools import compress
import string
import logging

class AuxFuncPack:
    # package of custom functions

    def fasta_to_list(self, fasta_fn):
        ### convert .fasta file into a list
        filepath = Path.cwd() / fasta_fn
        # original list format: [(name, seq)]
        fasta_list = list(FastaIO.SimpleFastaParser(open(filepath)))
        # converting to list of lists (instead of list of tuples)
        fasta_list = list(map(list, fasta_list))
        # replace underscores for spaces and upper all chars
        for fasta_idx in range(0, len(fasta_list)):
            fasta_list[fasta_idx][0] = fasta_list[fasta_idx][0].replace('_', ' ')
            fasta_list[fasta_idx][1] = fasta_list[fasta_idx][1].upper()
        # check if all sequences have the same size
        sizes_list = []
        for fasta_idx in range(0, len(fasta_list)):
            sizes_list.append(len(fasta_list[fasta_idx][1]))
        if not all(x == sizes_list[0] for x in sizes_list):
            logging.getLogger().info(f'WARNING: .fasta file has inconsistency: {fasta_fn}')

        return fasta_list
    
    def add_alert_on_df(self, df_alert, seq_name, col_num, alert_type_str):
        df_alert = df_alert.append(
            {
                'SeqName': seq_name,
                'ColNum': col_num+1,
                'AlertType': alert_type_str
            }
        , ignore_index=True)

        return df_alert

    def deep_searcher(self, fasta_folder, fasta_list, col_num, df_alert, searchable_keyphrase):
        # create local root
        loc_root = AnyNode(name='LocRoot', codon='LocRootCodon')
        # create nodes from column number
        for row in range(0, len(fasta_list)):
            AnyNode(
                name=fasta_list[row][0],
                codon=fasta_list[row][1][col_num:col_num+3],
                parent=loc_root
            )
        # run through nodes
        for node in loc_root.children:
            # check if codon is possibly searchable
            codon_unknown_chars = set(node.codon).difference(set(['A', 'C', 'T', 'G']))
            if len(codon_unknown_chars) != 0:
                isCodonWithSpecialChar = (any([x in codon_unknown_chars for x in ['-', '?']]))
                if searchable_keyphrase in node.name and not isCodonWithSpecialChar:
                    # non-gap searchable codon
                    fasta_dict = dict(fasta_list)
                    # check previous number of gaps from sequence
                    num_gaps = fasta_dict[node.name][:col_num].count('-')
                    # shift column number to the correct one
                    shifted_col_num = col_num-num_gaps
                    # get fasta_list of this node's original sequence
                    deeper_fn = node.name.replace((' ' + searchable_keyphrase),'') + '.fasta'
                    deeper_path = str(fasta_folder) + '/' + deeper_fn
                    deeper_list = self.fasta_to_list(deeper_path)
                    # go deeper
                    deeper_result = self.deep_searcher(
                        fasta_folder, deeper_list, shifted_col_num, df_alert, searchable_keyphrase
                    )
                    deeper_result[0].parent = node
                    df_alert = deeper_result[1]
                else:
                    # non-searchable codon, increment on df_alert
                    df_alert = self.add_alert_on_df(
                        df_alert, 
                        node.name,
                        col_num, 
                        'Pure ' + node.codon
                    )        

        return loc_root, df_alert

    def get_codons_perc_dict(self, root, codons_list):
        ### convert list of codons to dict (codon -> its perc)
        # get list of codons levels
        codons_levels = [[node.codon for node in children] for children in LevelOrderGroupIter(
            root,
            filter_=lambda n: n.codon != 'LocRootCodon'
        )]
        # clear any empty lists (parent roots)
        codons_levels = [x for x in codons_levels if x]
        codons_dict = {}
        for target_codon in codons_list:
            total_perc = 0
            deepness_perc = 1
            for level in codons_levels:
                codon_perc_on_lvl = (level.count(target_codon)/len(level))
                total_perc = total_perc + (codon_perc_on_lvl)*deepness_perc
                num_of_deepables = sum([len(set(codon).difference(set(['A', 'C', 'T', 'G', '-']))) != 0 for codon in level])
                deepables_perc_on_lvl = (num_of_deepables/len(level))
                deepness_perc = deepness_perc * deepables_perc_on_lvl
            codons_dict[target_codon] = total_perc

        return codons_dict

    def get_mutations_perc_dict(self, aminos_dict, codons_dict, df_codons):
        ### detect mutation types between codons
        muts_dict = {}
        # case 1: silent mutation (Sil) -> no amino change between diff codons
        muts_dict = self.add_sil_perc_to_dict(aminos_dict, codons_dict, df_codons, muts_dict)
        # case 2: missense mutation (Mis) -> amino change between diff codons
        muts_dict = self.add_mis_perc_to_dict(aminos_dict, df_codons, muts_dict)
        # case 3: nonsense mutation (Non) -> stop codons between diff codons
        muts_dict = self.add_non_perc_to_dict(aminos_dict, muts_dict)
        
        return muts_dict

    def add_sil_perc_to_dict(self, aminos_dict, codons_dict, df_codons, muts_dict):
        # best-case (lim 0): only one different codon 
        # worst-case (1): all possible codons for the same amino, in equal proportions
        local_sil_dict = {}
        for amino_name, amino_perc in aminos_dict.items():
            codons_mask = [
                df_codons.loc[df_codons['Codon'] == codon].Amino.iat[0] == amino_name
                for codon in codons_dict
            ]
            num_existent_codons = sum(codons_mask)
            if num_existent_codons is 1:
                local_sil_dict[amino_name] = 0
                continue
            num_possible_codons = df_codons.loc[df_codons['Amino'] == amino_name].shape[0]
            codon_diversity_perc = num_existent_codons/num_possible_codons
            wc_perc = 1/num_possible_codons
            dists_real_wc = list(compress([
                abs((codon_perc/amino_perc)-wc_perc)
                for codon_name, codon_perc in codons_dict.items()
            ], codons_mask))
            dists_sum = sum(dists_real_wc)
            local_sil_dict[amino_name] = codon_diversity_perc*(1/(dists_sum+1))
        sil_perc = sum([
            local_sil_perc*aminos_dict[local_sil_name]
            for local_sil_name, local_sil_perc in local_sil_dict.items()
        ])
        if sil_perc > 0: muts_dict['Sil'] = sil_perc

        return muts_dict

    def add_mis_perc_to_dict(self, aminos_dict, df_codons, muts_dict):
        # best-case (lim 0): only one different amino generated through a different codon
        # worst-case (1): all possible aminos being generated, in equal proportions
        local_mis_dict = {}
        num_existent_aminos = len(aminos_dict)
        if num_existent_aminos > 1:
            num_possible_aminos = len(df_codons.Amino.unique())
            amino_diversity_perc = num_existent_aminos/num_possible_aminos
            wc_perc = 1/num_possible_aminos
            for amino_name, amino_perc in aminos_dict.items():
                local_mis_dict[amino_name] = amino_diversity_perc*(1/(abs(amino_perc-wc_perc)+1))
            mis_perc = sum([
                local_mis_perc*aminos_dict[local_mis_name]
                for local_mis_name, local_mis_perc in local_mis_dict.items()
            ])
            if mis_perc > 0: muts_dict['Mis'] = mis_perc

        return muts_dict

    def add_non_perc_to_dict(self, aminos_dict, muts_dict):
        # best-case (lim 0): only one stop codon 
        # worst-case (1): half of codons are stop codons
        if '*' in aminos_dict:
            stop_codon_perc = aminos_dict['*']
            if stop_codon_perc > 0 and stop_codon_perc <= 0.5:
                non_perc = 2*stop_codon_perc
            elif stop_codon_perc > 0.5 and stop_codon_perc <= 1:
                non_perc = -2*stop_codon_perc + 2
            if non_perc > 0: muts_dict['Non'] = non_perc
        
        return muts_dict

    def get_aminos_from_codons(self, codons_dict, df_aminos):
        ### translate codons into aminos    
        aminos_dict = {}
        for codon_name, codon_perc in codons_dict.items():
            codon_amino = df_aminos.loc[df_aminos['Codon'] == codon_name, 'Amino'].iat[0]
            aminos_dict[codon_amino] = aminos_dict.get(codon_amino, 0) + codon_perc
        return aminos_dict

    def get_polarities_perc_dict(self, aminos_dict, df_pols):
        ### get dict of polarities within aminos list
        # get list of tuples (pol_type -> perc)
        list_percs = []
        for curr_pol in range(0, df_pols.shape[0]):
            pol_amino_list = list(df_pols.Amino.at[curr_pol])
            for curr_amino in list(aminos_dict.items()):
                if curr_amino[0] in pol_amino_list:
                    list_percs.append((df_pols.Type.at[curr_pol], curr_amino[1]))
        # convert into unified dict
        pols_dict = {}
        for key, value in list_percs:
            pols_dict[key] = pols_dict.get(key, 0) + value        

        return pols_dict

    def get_pol_score(self, pols_dict, df_pols):
        ### calculate polarity score
        # convert dict into list of tuples
        pols_percs = list(pols_dict.items())
        # get sum of current scores
        sum_scores = 0
        for curr_pol in pols_percs:
            sum_scores += df_pols.loc[df_pols['Type'] == curr_pol[0], 'Score'].values[0]
        # calculate
        pol_list_size = len(pols_percs)
        if pol_list_size <= 1:
            pol_score = 0
        else:
            # get minimal value of perc
            min_pols = min(pols_percs, key = lambda t: t[1])[1]
            pol_score = sum_scores*3 + pol_list_size*0.6 + min_pols

        return pol_score

    def get_gen_score(self, pol_score, muts_dict):
        ### calculate general score (based on mutation and polarity)
        mut_score = 0
        for muts_name, muts_perc in muts_dict.items():
            if muts_name is 'Sil': mut_score += muts_perc*0.1
            if muts_name is 'Mis': mut_score += muts_perc*200
            if muts_name is 'Non': mut_score += muts_perc*200
        pol_score_weight = 0.01
        gen_score = (1-pol_score_weight)*mut_score + pol_score_weight*pol_score

        return gen_score

    def round_dict_values(self, old_dict, digits, isCompareNeeded):
        decimal_limit = 10**(-digits)
        new_dict = {}
        sum_new_values = 0
        for curr_key, curr_value in old_dict.items():
            new_value = round(curr_value, digits)
            new_dict[curr_key] = new_value
            sum_new_values += new_value
        if sum_new_values == 1-decimal_limit and isCompareNeeded:
            min_key = min(new_dict, key=new_dict.get)
            new_dict[min_key] = round(new_dict[min_key] + decimal_limit, digits)
        elif sum_new_values == 1+decimal_limit and isCompareNeeded:
            max_key = max(new_dict, key=new_dict.get)
            new_dict[max_key] = round(new_dict[max_key] - decimal_limit, digits)
            
        return new_dict