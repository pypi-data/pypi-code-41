import os
import yaml
import subprocess

ENV_FILE_DIR = os.path.join(os.environ['HOME'], '.abode', 'env_files')
if not os.path.isdir(ENV_FILE_DIR):
    os.mkdir(ENV_FILE_DIR)

def env_files():
    return os.listdir(ENV_FILE_DIR)

def env_file(name):
    return os.path.join(ENV_FILE_DIR, name + '.yml')

def save_env(env):
    with open(env_file(env['name']), 'w') as f:
        yaml.dump(env, f, Dumper=yaml.SafeDumper)

def load_env(path=None):

    if path:
        with open(path, 'r') as f:
            env = yaml.load(f, Loader=yaml.SafeLoader)
        return env

    env_name = os.environ['CONDA_DEFAULT_ENV']

    with open(env_file(env_name), 'r') as f:
        env = yaml.load(f, Loader=yaml.SafeLoader)

    return env

def export():
    subprocess.run(['cat', env_file(os.environ['CONDA_DEFAULT_ENV'])])

def import_env(path):
    # Load from file, then save to Abode environment directory
    env = load_env(path)
    save_env(env)

    return env