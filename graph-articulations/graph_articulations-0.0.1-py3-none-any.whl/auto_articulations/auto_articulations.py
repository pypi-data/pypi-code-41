from pathlib import Path
from graph_articulations.config import GRAPH_ART_ROOT
from graph_articulations.data import categorical_list_of_models
from graph_articulations import list_of_models_with_issues, line_br
import os
import simplejson as json



def find_mpid_source_combo(sim_dir=None, input_cat=None, output_path=None):
    """
    Writes comprehensive nested dictionary { (key) Model : (value) { (key) mpid : (value) [source_mpid1, ... , source_mpidn]}
    path_to_test_models = [Path(sim_dir, model) for model in test_set] to json file.

    :param sim_dir: root path of model similarity information. If not provide, then uses ARTICULATIONS_SIM_DIR variable
    :param eval_dir: path to the evaluation directory
    :param output_path: path to write comprehensive json file too
    """

    if sim_dir is None:
        sim_dir = os.environ["ARTICULATIONS_SIM_DIR"]
        assert sim_dir is not None, 'ARTICULATIONS_SIM_DIR is not set as an environment variable'

    if input_cat is None: cat_dict = categorical_list_of_models(input_cat)
    keys = [k for k, _ in cat_dict.items()]

    # First level of nested dictionary { (key) Model : (value) { (key) mpid : (value) [source_mpid1, ... , source_mpidn]}
    path_to_test_models = [Path(sim_dir, model) for key in keys for model in cat_dict[key]]
    mpid_dict = {}

    bad_models = list_of_models_with_issues()
    skipped = []

    # Iterate through every subdirectory that test models posses
    for model_path in path_to_test_models:
        model = model_path.name
        mpid_dict[model] = []
        mpids_source_mpids = []

        if model in bad_models:
            print(f'Skipping {model}.... it has been blacklisted')
            skipped.append(model)
            continue

        for part_path in model_path.iterdir():
            mpid = model + '-' + part_path.name
            print(f'Getting sources for mpid: {mpid}...')

            for source_model in part_path.iterdir():
                # Find every json file that references source models
                # Read pid from current file
                with source_model.open('r') as read_file:
                    source_info = json.load(read_file)
                    read_file.close()

                # Get mpid and source_mpid from path
                source_mpid = source_model.name[:-5] + '-' + str(source_info[-1]['pid2'])
                mpids_source_mpids.append(source_mpid)

            mpid_dict[model].append({mpid: mpids_source_mpids})

    if output_path is None:
        output_path = GRAPH_ART_ROOT / 'considered_mpids_and_source_mpids.json'

    with open(output_path, 'w') as json_file:
        json.dump(mpid_dict, json_file)
        json_file.close()

    print(f'Skipped the following: \n{line_br}\n{skipped}')
    print('Done :)')


if __name__ == '__main__':
    find_mpid_source_combo()
