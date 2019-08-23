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
        parser = argparse.ArgumentParser(description='Analyse polarity on all protein alignment .fasta files from a target.')
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
        df_pol_results = DataFrame(columns=['ColNum', 'PossibleAminos', 'PossiblePols', 'PolScore'])
        df_alert_results = DataFrame(columns=['SeqName', 'ColNum', 'AlertType'])
        csv_path = PurePath(__file__).parent.parent / 'data' / 'pols.csv'
        df_pols = read_csv(csv_path)
        # get list of unknown and known aminos
        [unknown_aminos, known_aminos] = auxf_handler.get_lists_aminos(df_pols)
        # execute deep searcher on each column from .fasta target file
        number_columns = len(target_list[0][1]) # number of chars on sequence
        isDebugModeActive = logging.getLogger().isEnabledFor(logging.DEBUG)
        for current_col in tqdm(range(0, number_columns), disable=not isDebugModeActive):
            root, df_alert_results = auxf_handler.deep_searcher(
                target_folder, target_list, current_col, df_alert_results, unknown_aminos, searchable_keyphrase
            )
            # get root list of elements
            amino_leaves = []
            for leaf in root.leaves:
                if leaf.amino in known_aminos or leaf.amino in unknown_aminos:
                    amino_leaves.append(leaf.amino)
                else:
                    # invalid char, increment on df_alert_results
                    df_alert_results = auxf_handler.add_alert_on_df(
                        df_alert_results,
                        leaf.name,
                        current_col,
                        'Unlisted Char ' + leaf.amino
                    )
            # remove still unknown aminos
            amino_leaves = [x for x in amino_leaves if x not in unknown_aminos]
            # unify list
            unified_list = list(set(amino_leaves))
            # check length
            if len(unified_list) > 1:
                # get aminos percentages dict
                aminos_dict = auxf_handler.get_aminos_perc_dict(root, unified_list, unknown_aminos)
                # get polarities percentages dict
                pols_dict = auxf_handler.get_polarities_perc_dict(aminos_dict, df_pols)
                # get polarity score
                curr_pol_score = auxf_handler.get_pol_score(pols_dict, df_pols)
                # round dict values
                aminos_dict = auxf_handler.round_dict_values(aminos_dict, 5, True)
                pols_dict = auxf_handler.round_dict_values(pols_dict, 5, True)
                # increment on df_pol_results
                df_pol_results = df_pol_results.append(
                    {
                        'ColNum': current_col+1,
                        'PossibleAminos': aminos_dict,
                        'PossiblePols': pols_dict,
                        'PolScore': curr_pol_score
                    }, ignore_index=True
                )
        results_df_list = [df_pol_results, df_alert_results]
        return results_df_list

    def start_export(self, results_df_list, report_type, report_name, report_path):
        # export dfs
        DfExporter().export_dfs(
            results_df_list, report_type, report_name, report_path
        )
    
    def set_debug_mode(self, isActive):
        curr_level = logging.DEBUG if isActive else logging.INFO
        logging.getLogger().setLevel(curr_level)