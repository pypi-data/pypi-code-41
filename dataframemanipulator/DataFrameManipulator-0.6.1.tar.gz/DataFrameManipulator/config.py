NOT_PROCESSORS_METHOD = ['NOT_PRO', 'FILTER_ACTIONS', 'FILTER_MATCH_MODES',
                         'FILTER_NORM_MODES', '__init__', '__str__',
                         '__repr__', 'steps', 'components', 'df', 'add_step', 'add_component', 'reset_df',
                         'remove_step', 'run_steps', 'rearrange_steps',
                         '_run_steps', 'remove_component', 'run_components', 'rearrange_components',
                         '_run_components', 'processors_list', '__class__', '__delattr__',
                         '__dict__', '__dir__', '__doc__', '__eq__',
                         '__format__', '__ge__', '__getattribute__', '__gt__',
                         '__hash__', '__init__', '__init_subclass__',
                         '__le__', '__lt__', '__module__', '__ne__', '__new__',
                         '__reduce__', '__reduce_ex__', '__repr__',
                         '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
                         '__weakref__', '_filter_value_remove_rows',
                         '_filter_value_keep_rows', '_apply_mode',
                         '_convert_value_to_col_type', 'deactivate_step',
                         'activate_step', 'deactivate_component',
                         'activate_component', '_check_column_existence', 'statistics', 'errors', '_verify_params',
                         '_apply_model_step', '_save_model_to_s3', '_load_model_from_s3', '_download_s3', '_put_s3']

# : Processors methods

COMMON_PROCESSORS = ['delete', 'rename', 'set_as_index', 'move_to', 'move_after', 'filter_rows_on_value',
                     'filter_rows_on_numerical_range']
PROCESSING_PROCESSORS = ['index', 're_sample', 'normalize', 'standardize', 'smooth', 'missing_values', 'reset_index']

# : Parameters Configurations

FILTER_ACTIONS = ["Remove rows", "Keep these rows only"]
FILTER_NORM_MODES = ['Exact', 'Ignore Case', 'Normalize']
