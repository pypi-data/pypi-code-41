### Deep Codon Mutation Analyser (DCMA)
### Copyright (c) 2019 Jan Marans Agnella Justi & Mariana de França Costa

from ._src import _core_methods

_cmh = _core_methods.CoreMethods()

def _main():
    _cmh.start_main()

def run(target_path, searchable_keyphrase='consensus sequence'):
    return _cmh.start_run(target_path, searchable_keyphrase)

def export(results_df_list, report_type, report_name, report_path='.'):
    _cmh.start_export(results_df_list, report_type, report_name, report_path)

def set_debug_mode(isActive):
    _cmh.set_debug_mode(isActive)