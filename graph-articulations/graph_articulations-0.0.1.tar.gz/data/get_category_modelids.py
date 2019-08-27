from pathlib import Path
from graph_articulations.config import *
import pandas as pd
import simplejson as json
import argparse
import shutil

parser = argparse.ArgumentParser(description='Get model ids by category')
parser.add_argument('--out_path', default=None, help='path of desired output json')
parser.add_argument('--models_csv', default=None, help='path to scene-toolkit/server/static/data/suncg/suncg.planner5d.models.full.csv')
parser.add_argument('--category_json', default=None, help='path to a json list of categories')
parser.add_argument('--docker_home', default='/home/ham', help='path to desired working dir')
parser.add_argument('--model_root', default=None, help='path to model meshes')
parser.add_argument('--part_root', default=None, help='path to parts')
parser.add_argument('--conn_root', default=None, help='path to connectivity graphs')

args = parser.parse_args()

docker_home = Path(args.docker_home)
home = docker_home if docker_home.exists() else Path.home()

json_output_path = GRAPH_ART_ROOT / 'category_to_models.json' if args.out_path is None else args.out_path
model_csv_path = home / 'scene-toolkit/server/static/data/suncg/suncg.planner5d.models.full.csv' if args.models_csv is None else args.model_csv_path
categories_json_path = GRAPH_ART_ROOT / 'categories.json' if args.category_json is None else args.category_json

models_df = pd.read_csv(model_csv_path)

# List of categories to collect model ids for
categories = None
with open(categories_json_path, 'r') as categories_json: categories = json.load(categories_json)


def get_models_from_category(category_name: str):
    """
    category_name: Name of the category that we want to collect the models ids for
    
    Returns: List of model ids that belong to category_name
    """
    index_where_category = models_df.category.str.contains(category_name)
    category_indexes = models_df.index[index_where_category]
    category_df = models_df.iloc[category_indexes]
    return category_df.id.values.tolist()


def copy_all_model_info(target_path: str = None):
    """
    Use to move data from separate directories to one place
    :param target_path: Destination path of copy
    """
    if target_path is None:
        target_path = GRAPH_ART_ROOT / 'articulation_data'

    target_path = Path(target_path)
    if not target_path.exists(): Path.mkdir(target_path)

    for category, models in category_to_models.items():
        for model in models:
            # if model == "s__788":
            #     continue

            model_suffix = f'/{model}.obj'
            part_suffix = f'/{model}.parts.json'
            conn_suffix = f'/{model}.artpre.json'

            model_path = str(MODEL_ROOT / model) + model_suffix
            part_path = str(PART_ROOT / model) + part_suffix
            connectivity_path = str(CONNECTIVITY_ROOT) + conn_suffix
            # if Path(model_path).exists() and Path(part_path) and Path(conn_suffix):
            shutil.copy(model_path, str(target_path ))
            shutil.copy(part_path, str(target_path ))
            shutil.copy(connectivity_path, str(target_path ))


if __name__ == '__main__':
    part_root = PART_ROOT if args.part_root is None else args.part_root
    connectivity_root = CONNECTIVITY_ROOT if args.conn_root is None else args.conn_root
    model_root = MODEL_ROOT if args.model_root is None else args.model_root

    # Iterate through category and store all outputs in a comprehensive dictionary
    # Dump this dictionary to JSON for future use
    category_to_models = {cur_category: get_models_from_category(cur_category) for cur_category in categories}
    with open(json_output_path, 'w') as json_file:
        json.dump(category_to_models, json_file)

    # Relevant paths for copying function
    # Copy all relevant info to a single directory
    # copy_all_model_info()
