# coding: utf-8

from deployv.helpers import utils
import distutils.spawn
from docker import errors, APIClient as Client
import json
import logging
from os import environ, path, makedirs, chmod
import re
import requests
import shlex
import subprocess
import sys
import time
from urllib3.exceptions import ReadTimeoutError


_logger = logging.getLogger('deployv.' + __name__)
_cli = Client(timeout=7200)
TO_SCAN = ['git.vauxoo.com',
           'github.com']


def pull_images(images):
    """ Pulls images needed for the build and test process """
    for image in images:
        _logger.info('Pulling: %s', image)
        _cli.pull(image)
    return images


def check_env_vars(*args, **kwargs):
    missing = []
    not_required = ['psql_image', 'push_image']
    for key in args:
        if key not in not_required and not (key.upper() in environ and environ[key.upper()]):
            missing.append(key.upper())
    for key in kwargs:
        if not (key.upper() in environ and environ[key.upper()]):
            if kwargs[key]:
                environ[key.upper()] = str(kwargs[key])
            elif key not in not_required:
                missing.append(key.upper())
    assert not missing, (
        "Some environment variables were not found: {keys}".format(
            keys=", ".join(missing)
        ))


def get_main_app(config):
    if config.get('install', False):
        _logger.warning('Deprecation warning: you should not use INSTALL env var, replace it with MAIN_APP instead')
        return config.get('install')
    return config.get('main_app', False)


def generate_image_name(name):
    """ Generate the base image name using the ref name but cleaning it before,
    ATM only removes "." and "#" from the title to avoid issues with docker naming
    convention """
    res = re.sub(r'[\.#\$\=\+\;\>\,\<,\&\%]', '', name)
    res = re.sub(r'-_', '_', res)
    return res.lower()


def run_build_image(config):
    _logger.info('Building image')
    cmd = ('deployvcmd build -b {branch} -u {url} -v {version} -i {image} -O {repo}#{odoo_branch} -T {tag}'
           .format(branch=config['ci_commit_ref_name'], url=config['ci_repository_url'], repo=config['odoo_repo'],
                   odoo_branch=config['odoo_branch'], version=config['version'], image=config['base_image'],
                   tag=config['instance_image']))
    try:
        subprocess.check_call(shlex.split(cmd))
    except subprocess.CalledProcessError:
        _logger.exception('Could not build the image, please read the log above')
        sys.exit(1)
    images = _cli.images(config['instance_image'])
    image_sha = images[0].get('Id')
    short_id = image_sha.split(':')[1][:10]
    config.update({
        'image_tag': short_id,
    })


def clear_images(config):
    images = [config['instance_image'], config['postgres_image'], ]
    for image in images:
        try:
            _logger.info('Removing image %s', image)
            _cli.remove_image(image)
        except errors.APIError as error:
            if 'No such image' in error.explanation:
                pass
        _logger.info('Image %s deleted', image)


def clean_containers(config):
    """ Cleans any running container related to the same build to avoid any conflicts """
    containers = _cli.containers(all=True, filters={'name': config['base_name']})
    for container in containers:
        try:
            _logger.info('Removing container %s', container.get('Name', container.get('Names')[0]))
            _cli.remove_container(container['Id'], force=True)
        except errors.NotFound:
            _logger.info('Container %s does not exist', container.get('Name', container.get('Names')[0]))


def reciveSignal(signalNumber, frame):
    clean_containers()
    clear_images()
    sys.exit(0)


def push_image(config, image_name, image_tag):
    _logger.info('Pushing image %s to %s:%s', image_name, config['image_repo'], image_tag)
    _cli.tag(image_name, config['image_repo'], tag=image_tag)
    if is_docker_login(config):
        _logger.info('Logging in to push: %s', config['docker_repo'])
        _cli.login(config['docker_user'], config['docker_password'], registry=config['docker_repo'])
    for attempt in range(4):
        try:
            for result in _cli.push(config['image_repo'], tag=image_tag, stream=True):
                result = json.loads(utils.decode(result))
                if result.get('error'):
                    _logger.error(result.get('error'))
                    sys.exit(1)
            else:
                break
        except ReadTimeoutError as error:
            if 'Read timed out' in error.message and attempt < 3:
                _logger.warn('An error raised while pushing the image, retrying (%s / 3)', attempt+1)
            else:
                raise

    _logger.info('Image pushed correctly')


def notify_orchest(config, is_latest=False):
    image_name = '{image}:{tag}'.format(image=config['image_repo'], tag=config['image_tag'])
    res = requests.post(
        config['orchest_registry'], data=json.dumps({
            'image_name': image_name, 'is_latest': is_latest, 'branch_name': config['ci_commit_ref_name'],
            'job_id': config['ci_job_id'], 'project_id': config['ci_project_id'],
            'commit': config['ci_commit_sha'][:7], 'customer_id': config['customer_img']}),
        headers={'Content-Type': 'application/json', 'Orchest-Token': config['orchest_token']})
    if res.status_code != 200:
        _logger.error('Failed to notify orchest about the new image: %s', res.text)
        sys.exit(1)
    data = res.json()
    if data.get('error'):
        _logger.error('Failed to notify orchest about the new image: %s',
                      data.get('error').get('data', {}).get('name'))
        sys.exit(1)
    _logger.info('Successfully notified orchest about the new image: %s', image_name)


def get_value(var_name, **kwargs):
    return kwargs[var_name] if var_name in kwargs else environ[var_name.upper()]


def get_config(**kwargs):
    rand_str = 'hd103sl'
    res = {}
    for k, v in environ.items():
        res.update({k.lower(): v})

    for key in kwargs:
        res.update({key.lower(): get_value(key, **kwargs)})

    res.update({'private_deploy_key': res.get('private_deploy_key', False)})
    img_name = generate_image_name('{0}_{1}'.format(
        res['ci_commit_ref_name'], res['ci_job_id']))
    res.update({'base_name': img_name})

    if res.get('psql_image'):
        postgres_image = res.get('psql_image')
    else:
        postgres_image = 'vauxoo/docker-postgresql:{0}-ci'.format(res.get('psql_version', '9.6'))
    res.update({'postgres_image': postgres_image})

    customer = res.get('customer', res.get('ci_project_name', res.get('main_app'))).strip()
    version_tag = res.get('version').replace('.', '')
    customer_img = '{customer}{ver}'.format(customer=customer,
                                            ver=version_tag)
    if not res.get('image_repo', False) and not res.get('image_tag', False):
        image_repo = '{url}/{image}'.format(url=res.get('image_repo_url'),
                                            image=customer_img)
        res.update({'image_repo': image_repo})
        instance_image = generate_image_name('instance{0}_{1}'.format(
            res.get('base_name'), res.get('ci_pipeline_id')))
    else:
        instance_image = '{}:{}'.format(res['image_repo'], res['image_tag'])

    res.update({'instance_image': instance_image})

    res.update({
        'customer': customer,
        'version_tag': version_tag,
        'customer_img': customer_img,
        'container_name': '{}_instance_{}_{}'.format(res['base_name'], res['ci_pipeline_id'], rand_str)
    })

    res.update({'docker_repo': res.get('docker_repo', 'quay.io')})
    res.update({'image_repo_url': res.get('image_repo_url', 'quay.io/vauxoo')})
    res.update({'postgres_container': 'postgres{0}_{1}_{2}'.format(res['base_name'], res['ci_pipeline_id'], rand_str)})
    return res


def docker_login(config):
    """ Execute docker login from the actual console because whe done via the api they won't persist """
    cmd = 'sh -c "echo \'{passw}\' | docker login --username \'{login}\' --password-stdin {repo}"'.format(
        passw=config['docker_password'],
        login=config['docker_user'],
        repo=config['docker_repo']
    )
    subprocess.Popen(shlex.split(cmd))


def check_docker():
    """ Checks if the docker binary is present in the running environment """
    return distutils.spawn.find_executable("docker")


def is_docker_login(config):
    """ Check if we have all we need to docker login (via cli or api), that is:

    - We have docker binary available
    - We have the env vars properly set (DOCKER_PASSWORD and DOCKER_USER)"""
    return check_docker() and config.get('docker_password', False) and config.get('docker_user', False)


def scan_keys(folder):
    """ Performs a ssk-key scan in the list of hosts and add the keys to the
    known_hosts files

    :param folder: The folder where the file will be stored
    """
    known_hosts = path.join(folder, 'known_hosts')
    with open(known_hosts, 'a') as known_file:
        for host in TO_SCAN:
            keys = subprocess.check_output(['ssh-keyscan', host], stderr=subprocess.STDOUT)
            for line in utils.decode(keys).split('\n'):
                clean = line.strip()
                if clean:
                    known_file.write(clean + '\n')
    subprocess.check_call(['ls', '-l', folder])


def add_private_key(key, folder):
    """ Generates the id_rsa file if it doesn't exits with the proper
    format and permissions

    :param key: The key content
    :param folder: The folder where the id_rsa file will be stored
    """
    ssh_file = path.join(folder, 'id_rsa')
    if path.isfile(ssh_file):
        _logger.info('The id_rsa file already exists, nothing to do')
        return
    with open(ssh_file, 'w') as ssh_key:
        ssh_key.write(key)
    try:
        subprocess.check_call(['dos2unix', ssh_file])
    except subprocess.CalledProcessError:
        _logger.error('You need to install dos2unix to check the key')
    chmod(ssh_file, 0o0600)


def check_ssh_folder():
    """ Check if the folder exists and create it

    :return: The full path to the .ssh folder
    """
    home_path = path.expanduser(path.join('~', '.ssh'))
    if not path.isdir(home_path):
        makedirs(home_path)
    return home_path


def check_credentials(config):
    _logger.info('Check ssh folder')
    ssh_folder = check_ssh_folder()
    if config['private_deploy_key']:
        _logger.info('Adding private key')
        add_private_key(config['private_deploy_key'], ssh_folder)

    _logger.info('Scan hosts keys')
    scan_keys(ssh_folder)

    if is_docker_login(config):
        _logger.info('Logging in %s', config['docker_repo'])
        docker_login(config)


def prepare(**kwargs):
    check_env_vars(**kwargs)
    config = get_config(**kwargs)
    check_credentials(config)
    return config


def save_imagename(config):
    if not path.isdir(config["ci_commit_ref_name"]):
        makedirs(config["ci_commit_ref_name"])
    filename = path.join(config["ci_commit_ref_name"], "image_name.env")
    with open(filename, "w") as f:
        f.write("export IMAGE_REPO={}\n".format(config['image_repo']))
        f.write("export IMAGE_TAG={}\n".format(config['image_tag']))


def start_instance(config):
    env = {
        "DB_USER": "odoo",
        "DB_PASSWORD": "odoo",
        "DB_HOST": config['postgres_container'],
        "ODOO_CONFIG_FILE": "/home/odoo/.openerp_serverrc"
    }
    for env_var in ['COUNTRY', 'LANGUAGE']:
        env.update({env_var: environ.get(env_var, "")})
    links = {
        config['postgres_container']: config['postgres_container']
    }
    host_config = _cli.create_host_config(links=links)
    _logger.info('Starting container %s', config['container_name'])
    _logger.debug('Env vars %s', json.dumps(env, sort_keys=True, indent=4))
    container = _cli.create_container(image=config['instance_image'],
                                      name=config['container_name'],
                                      environment=env,
                                      host_config=host_config)
    _cli.start(container=container.get('Id'))
    _logger.info(container)


def start_postgres(config):
    _logger.info('Starting container %s', config['postgres_container'])
    container = _cli.create_container(image=config['postgres_image'],
                                      name=config['postgres_container'],
                                      environment={'POSTGRES_PASSWORD': 'postgres'})
    _cli.start(container=container.get('Id'))
    _logger.info(container)


def exec_cmd(container, cmd, user=None, stream=False):
    lines = []
    container_id = _cli.inspect_container(container).get('Id')
    _logger.debug('Executing command "{cmd}" in container "{con}".'.format(cmd=cmd, con=container))
    try:
        exec_id = _cli.exec_create(container_id, cmd, user=user)
    except errors.APIError as error:
        _logger.error('Error: %s', error.explanation)
        raise
    res = _cli.exec_start(exec_id.get('Id'), stream=stream)
    if stream:
        for line in res:
            line = utils.decode(line)
            _logger.info(line.strip('\n'))
            lines.append(line)
        return lines
    return utils.decode(res)


def create_postgres_user(config):
    cmd = "psql -c \"create user odoo with password 'odoo' createdb\""
    retry = 0
    while retry < 4:
        res = exec_cmd(config['postgres_container'], cmd, 'postgres')
        if 'could not connect to server' in res:
            retry += 1
            _logger.info('Waiting for the postgres container to start (retrying %s)', retry)
            time.sleep(3)
        else:
            break
    return res


def is_running(config):
    retry = True
    retries = 0
    while retry and retries <= 10:
        try:
            res = exec_cmd(config['instance_image'], 'supervisorctl status odoo')
        except errors.APIError:
            retries += 1
            _logger.warn('Container error, retrying %s', retries)
            time.sleep(5)
            continue
        _logger.info('is_running: %s', res.strip())
        if 'STARTING' in res or 'STOPPING' in res:
            _logger.warn('The Odoo process is in an intermediate state, retrying')
            time.sleep(5)
        elif 'RUNNING' in res:
            return True
        elif 'STOPPED' in res:
            return False
        elif res == '' or 'no such file' in res:
            retries += 1
            _logger.warn('Supervisor returned empty or not running yet, retrying %s', retries)
            time.sleep(5)
        else:
            retries += 1
            _logger.warn('Unknown state: %s', res)
            time.sleep(5)


def install_module(config):
    module = config['main_app']
    extra = ''
    if config.get('language', False):
        extra += ' --load-language={lang}'.format(lang=config.get('language'))
    install_wdemo = (
        "/home/odoo/instance/odoo/odoo-bin -d wdemo -i {mod}"
        "{extra} --stop-after-init".format(mod=module, extra=extra)
    )
    install_wodemo = (
        "/home/odoo/instance/odoo/odoo-bin -d wodemo -i {mod}"
        "{extra} --stop-after-init --without-demo=all".format(mod=module, extra=extra)
    )
    _logger.info('Verifying supervisorctl')
    is_running(config)
    _logger.info('Stopping odoo')
    exec_cmd(config['container_name'], 'supervisorctl stop odoo')
    _logger.info('\nInstalling %s with demo', module)
    _logger.debug('Command : %s', install_wdemo)
    wdemo_res = exec_cmd(config['container_name'], install_wdemo, 'odoo', stream=True)
    wdemo_log = resume_log(wdemo_res)
    _logger.info('\nInstalling %s without demo', module)
    _logger.debug('Command : %s', install_wodemo)
    wodemo_res = exec_cmd(config['container_name'], install_wodemo, 'odoo', stream=True)
    wodemo_log = resume_log(wodemo_res)
    show_log(wdemo_log[1], 'Installation with demo')
    show_log(wodemo_log[1], 'Installation without demo')
    if not wdemo_log[0] or not wodemo_log[0]:
        return False
    return True


def show_log(log, title):
    _logger.info('\n%s', title)
    _logger.info('='*20)
    _logger.info('+-- Critical errors %s', len(log.get('critical')))
    _logger.info('+-- Errors %s', len(log.get('errors')))
    _logger.info('+-- Import errors %s', len(log.get('import_errors')))
    _logger.info('+-- Warnings %s', len(log.get('warnings')))
    _logger.info('+-- Translation Warnings %s', len(log.get('warnings_trans')))
    _logger.info('='*20)


def resume_log(log_lines):
    """Gets the log lines from -u (modules or all) and parse them to get the totals
    according to the filters dict

    :param log_lines: each element of the list is a log line
    :return: dict with key filters as keys and a list with all matched lines
    """
    def critical(line):
        criteria = re.compile(r'.*\d\sCRITICAL\s.*')
        return criteria.match(line)

    def errors(line):
        criteria = re.compile(r'.*\d\sERROR\s.*')
        return criteria.match(line)

    def warnings_trans(line):
        criteria = re.compile(
            r'.*\d\sWARNING\s.*no translation for language.*')
        return criteria.match(line)

    def import_errors(line):
        criteria = re.compile(r'^ImportError.*')
        return criteria.match(line)

    def warnings(line):
        criteria = re.compile(r'.*\d\sWARNING\s.*')
        return criteria.match(line) and 'no translation for language' not in line

    filters = {
        'critical': critical,
        'errors': errors,
        'warnings': warnings,
        'warnings_trans': warnings_trans,
        'import_errors': import_errors
    }
    success = True
    res = {name: [] for name in filters}
    for line in log_lines:
        stripped_line = line.strip()
        for name, criteria in filters.items():
            if criteria(stripped_line):
                if name in ['critical', 'errors']:
                    success = False
                elif name == 'warnings' and 'Deprecated' in stripped_line:
                    success = False
                res.get(name).append(stripped_line)
                break
    return success, res


def run_image_tests(config):
    clean_containers(config)
    start_postgres(config)
    resp = create_postgres_user(config)
    _logger.info(resp)
    start_instance(config)
    res = install_module(config)
    clean_containers(config)
    return res
