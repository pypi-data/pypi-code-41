import stimela
import time
import json
import re

INPUT = "input"
OUTPUT = "output"
MSDIR = "msdir"

MANUAL = False
CONFIG = ''

if MANUAL:
    recipe = stimela.Recipe('Make Pipeline', ms_dir=MSDIR)
    stimela.register_globals()


def save_execution_time(data_dict, filename='recipes.json', root='output'):
    """Save execution time"""
    filename = '{}/{}_time-it.json'.format(root, filename.split('.')[0])
    try:
        # Extract data from the json data file
        with open(filename) as data_file:
            data_existing = json.load(data_file)
            data_existing.update(data_dict)
            data = data_existing
    except IOError:
        data = data_dict
    if data:
        with open(filename, 'w') as f:
            json.dump(data, f)


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    def atoi(text):
        return int(text) if text.isdigit() else text
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def json_dump(data_dict, filename='recipes.json', root='output'):
    """Dumps the computed dictionary into a json file.
    Parameters
    ----------
    data_dict : dict
        Dictionary with output results to save.
    filename : file
        Name of file to dump recipes for later runs
    root : str
        Directory to save output json file (default is current directory).
    Note
    ----
    If the `filename` file exists, it will be append, and only
    repeated recipes will be replaced.
    """
    filename = ('{:s}/{:s}'.format(root, filename))
    num = int(data_dict.keys()[0].split('_')[0])
    try:
        # TODO: This needs some reworking
        # Extract data from the json data file
        with open(filename) as data_file:
            data_existing = json.load(data_file)
            data_existing_copy = data_existing.copy()
            counter = 0
            data_keys = data_existing.keys()
            data_keys.sort(key=natural_keys)
            for d in data_keys:
                counter += 1
                cab_num = int(d.split('_')[0])
                cab_name = d.split('{}_'.format(cab_num))[-1]
                if cab_num >= num:
                    if d in data_dict.keys():
                        break
                    else:
                        if cab_num == num or cab_name != recipe_name:
                            data_existing.pop(d)
                        old_recipe = data_existing_copy.pop(d)
                        recipe_name = cab_name
                        data_existing['{:d}_{:s}'.format(counter+1, recipe_name)] = old_recipe
            data_existing.update(data_dict)
            data = data_existing
    except IOError:
        data = data_dict
    if data:
        with open(filename, 'w') as f:
            json.dump(data, f)


def get_data(filename='', root='output'):
    "Extracts data from the json data file"
    if filename:
        pass
    else:
        filename = 'recipes.json'
    filename = '{:s}/{:s}'.format(root, filename)
    with open(filename) as f:
        data = json.load(f)
    return data


def remove_cab(cab_id, filename='', root='output'):
    data = get_data(filename, root)
    try:
        data.pop(cab_id)
        print('{:s} cab was succesfully removed.'.format(cab_id))
    except KeyError:
        print('No cab with id: {:s}'.format(cab_id))
    filename = ('{:s}/{:s}'.format(root, filename))
    with open(filename, 'w') as data_file:
        json.dump(data, data_file)


def get_cab_num(num, recipes_file=''):
    if not num:
        try:
            data = get_data(recipes_file)
            data_keys = data.keys()
            data_keys.sort(key=natural_keys)
            for d in data_keys:
                cab_num = int(d.split('_')[0])
                num = cab_num+1
        except IOError:
            num = 1
    return num


def cab_function(recipe, name, num, parameters, recipes_file='', dump=True):
    """Generic cab function"""
    recipe_params = {}
    num = get_cab_num(num, recipes_file)
    prefix = recipes_file.split('/')[-1].split('.')[0] if recipes_file else 'recipes'
    step = "{}_{}_{}".format(prefix, num, name)
    cab = '{}_{}'.format(num, name)
    if name in ['ddfacet']:
        recipe.add("cab/{}".format(name),
                   step,
                   parameters,
                   input=INPUT,
                   output=OUTPUT,
                   shared_memory="150gb",
                   label="{}:: {}".format(step, cab))
    else:
        recipe.add("cab/{}".format(name),
                   step,
                   parameters,
                   input=INPUT,
                   output=OUTPUT,
                   label="{}:: {}".format(step, cab))
    recipe_params[cab] = parameters
    if dump:
        json_dump(recipe_params, recipes_file)
    else:
        pass


def wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped


def run_all(recipe, filename):
    DATA = dict()
    from timeit import timeit
    recipe_jobs = recipe.jobs
    filename = filename.split('/')[-1]
    for job in recipe_jobs:
        start_time = time.time()
        wrapped = wrapper(recipe.run, [job.name])
        t = timeit(wrapped, number=1)
        DATA[job.name] = t
        save_execution_time(DATA, filename)
