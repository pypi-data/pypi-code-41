import logging
from pathlib import Path
from StyleFrame import StyleFrame, Styler, utils

class DfExporter():
    def export_dfs(self, results_df_list, report_type, report_name, report_path):
        ### export alerts and pols df to csv/xls
        folder_path = Path.cwd() / report_path / report_name
        # extract dfs from list
        [df_pol_results, df_alert_results] = results_df_list
        # sorting by polscores
        df_pol_results = df_pol_results.sort_values(
            by=['PolScore'], ascending=False
        ).reset_index(drop=True)
        # check if any
        df_pols_size = df_pol_results.shape[0]
        df_alert_size = df_alert_results.shape[0]
        if (df_pols_size != 0 or df_alert_size != 0):
            # check user option
            if report_type == 'csv' or report_type == 'all':
                # option 1: export to csv format
                self.df_to_csv(df_pol_results, folder_path, 'pols')
                self.df_to_csv(df_alert_results, folder_path, 'alerts')
            if report_type == 'xls' or report_type == 'all':
                # option 2: export to xls format
                df_list = [df_pol_results, df_alert_results]
                sheetname_list = ['Polarity', 'Alerts']
                self.df_to_xls(df_list, sheetname_list, folder_path)
        else:
            logging.info('WARNING: Nothing to export. Both dfs are empty.')
        if (report_type not in ['csv', 'xls', 'all']):
            logging.info('WARNING: Invalid report type.')

    def df_to_csv(self, df, folder_path, fn_suffix):
        file_path = self.ext_remover(str(folder_path), '.fasta') + '-' + fn_suffix + '.csv'
        if not df.empty: df.to_csv(file_path, index=False)

    def df_to_xls(self, list_dfs, list_sheet_names, folder_path):
        # create list of styleframes based on dfs
        list_sfs = []
        for df in list_dfs:
            list_sfs.append(StyleFrame(df))
        # apply cell patterns if any
        if not list_dfs[0].empty: self.apply_highlights_pol_rows(list_sfs[0], list_dfs[0])
        # export
        file_path = self.ext_remover(str(folder_path), '.fasta') + '-report.xlsx'
        # best_fit factors
        StyleFrame.A_FACTOR = 6
        StyleFrame.P_FACTOR = 1.3
        with StyleFrame.ExcelWriter(file_path) as writer:
            for df_idx in range(0, len(list_sfs)):
                if not list_dfs[df_idx].empty:
                    list_sfs[df_idx].to_excel(
                        writer, 
                        sheet_name=list_sheet_names[df_idx], 
                        index=False,
                        best_fit=list(list_dfs[df_idx].columns.values)
                    )

    def apply_highlights_pol_rows(self, sf, df):
        # create masks based on row polarities
        pol_sets = df.PossiblePols.apply(lambda x: set(x.keys()))
        pp_mask = pol_sets.apply(lambda x: True if 'Pp' in x else False)
        pn_mask = pol_sets.apply(lambda x: True if 'Pn' in x else False)
        nc_mask = pol_sets.apply(lambda x: True if 'Nc' in x else False)  
        np_mask = pol_sets.apply(lambda x: True if 'Np' in x else False)      
        # list all cases and its colour code
        list_cases = []
        list_cases.append(tuple([sf[(pp_mask & pn_mask & nc_mask & np_mask)], 'a80000']))
        list_cases.append(tuple([sf[(pp_mask & pn_mask & (nc_mask ^ np_mask))], 'ff0000']))
        list_cases.append(tuple([sf[(pp_mask & pn_mask & ~(nc_mask | np_mask))], 'ff6400']))
        list_cases.append(tuple([sf[((pp_mask ^ pn_mask) & nc_mask & np_mask)], 'ff9200']))
        list_cases.append(tuple([sf[(pp_mask & ~pn_mask & (nc_mask ^ np_mask))], 'ffc800']))
        list_cases.append(tuple([sf[(~pp_mask & pn_mask & (nc_mask ^ np_mask))], 'e3b200']))
        list_cases.append(tuple([sf[~pp_mask & ~pn_mask & nc_mask & np_mask], 'fffe00']))
        list_cases.append(tuple([sf[sf.PolScore == 0], 'b3ff00']))
        # apply
        for case in list_cases:
            sf.apply_style_by_indexes(
                indexes_to_style=case[0],
                styler_obj=Styler(bg_color=case[1])
            )
        # end

    def ext_remover(self, name, ext):
        if name[-(len(ext)):] == ext: 
            name = name[:-(len(ext))]
        return name 