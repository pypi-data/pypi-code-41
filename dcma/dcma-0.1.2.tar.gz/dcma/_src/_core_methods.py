import argparse
import logging
from pathlib import PurePath
from pandas import DataFrame, read_csv
from tqdm import tqdm
from .helpers.auxfunc import AuxFuncPack
from .conv.export_dfs import DfExporter

logging.basicConfig(level=logging.INFO, format='%(message)s')

class CoreMethods:
    def start_main(self):
        # get options from user
        parser = argparse.ArgumentParser(description='Analyse mutation on all nucleotide alignment .fasta files from a target.')
        parser.add_argument(
            'target', help='Target .fasta file to be analysed.', type=str,
            metavar='TARGET'
        )
        parser.add_argument(
            'reportType', help='Output report file type.', type=str,
            choices=['csv', 'xls', 'all'], metavar='REPORTTYPE'
        )
        parser.add_argument(
            '--reportName', help='Output report custom file name.'
        )
        parser.add_argument(
            '--reportPath', help='Output report custom file path.'
        )
        parser.add_argument(
            '--searchKP', help='Custom keyphrase to detect searchable sequences.'
        )
        parser.add_argument(
            '--debug', help='Turn debug messages on.', action='store_true'
        )
        args = vars(parser.parse_args())
        # config logging
        self.set_debug_mode(args['debug'])
        # run
        searchable_keyphrase = args['searchKP'] if (args['searchKP'] is not None) else 'consensus sequence'
        results_df_list = self.start_run(args['target'], searchable_keyphrase)
        # export dfs
        report_path = args['reportPath'] if (args['reportPath'] is not None) else PurePath(args['target']).parent
        report_name = args['reportName'] if (args['reportName'] is not None) else PurePath(args['target']).name
        self.start_export(
            results_df_list, args['reportType'], report_name, report_path
        )
        logging.debug('Done.')
    
    def start_run(self, target_path, searchable_keyphrase):
        # run analyser
        logging.debug(f'Starting analysis for {target_path}')
        # create handler of custom functions
        auxf_handler = AuxFuncPack()
        # create list from .fasta target file
        target_folder = PurePath(target_path).parent
        target_list = auxf_handler.fasta_to_list(target_path)
        # create dfs
        df_mut_results = DataFrame(columns=['ColNum', 'PossibleCodons', 'PossibleMuts', 'PossiblePols', 'GenScore'])
        df_alert_results = DataFrame(columns=['SeqName', 'ColNum', 'AlertType'])
        df_codons = read_csv(PurePath(__file__).parent.parent / 'data' / 'codons.csv')
        df_pols = read_csv(PurePath(__file__).parent.parent / 'data' / 'pols.csv')
        # execute deep searcher on each column from .fasta target file
        number_codons = int(len(target_list[0][1])/3)
        isDebugModeActive = logging.getLogger().isEnabledFor(logging.DEBUG)
        for current_codon in tqdm(range(0, number_codons), disable=not isDebugModeActive):
            current_col = current_codon*3 # aiming codon's initial position
            root, df_alert_results = auxf_handler.deep_searcher(
                target_folder, target_list, current_col, df_alert_results, searchable_keyphrase
            )
            # get root list of elements
            codon_leaves = []
            for leaf in root.leaves:
                # keep only codons without special chars
                if len(set(leaf.codon).difference(set(['A', 'C', 'T', 'G']))) == 0:
                    codon_leaves.append(leaf.codon)
            # unify list
            unified_list = list(set(codon_leaves))
            if len(unified_list) > 1:
                # get codons percentages dict
                codons_dict = auxf_handler.get_codons_perc_dict(root, unified_list)  
                # get aminos from codons
                aminos_dict = auxf_handler.get_aminos_from_codons(codons_dict, df_codons)
                # get codons mutations dict             
                muts_dict = auxf_handler.get_mutations_perc_dict(aminos_dict, codons_dict, df_codons)
                # get polarities percentages dict
                pols_dict = auxf_handler.get_polarities_perc_dict(aminos_dict, df_pols)
                # get polarity score
                curr_pol_score = auxf_handler.get_pol_score(pols_dict, df_pols)
                # get general score
                curr_gen_score = auxf_handler.get_gen_score(curr_pol_score, muts_dict)
                # round dict values
                codons_dict = auxf_handler.round_dict_values(codons_dict, 5, True)
                muts_dict = auxf_handler.round_dict_values(muts_dict, 5, False)
                pols_dict = auxf_handler.round_dict_values(pols_dict, 5, True)
                # increment on df_mut_results
                df_mut_results = df_mut_results.append(
                    {
                        'ColNum': current_col+1,
                        'PossibleCodons': codons_dict,
                        'PossibleMuts': muts_dict,
                        'PossiblePols': pols_dict,
                        'GenScore': round(curr_gen_score, 5)
                    }, ignore_index=True
                )       
        results_df_list = [df_mut_results, df_alert_results]
        return results_df_list
    
    def start_export(self, results_df_list, report_type, report_name, report_path):
        # export dfs
        DfExporter().export_dfs(
            results_df_list, report_type, report_name, report_path
        )
    
    def set_debug_mode(self, isActive):
        curr_level = logging.DEBUG if isActive else logging.INFO
        logging.getLogger().setLevel(curr_level)