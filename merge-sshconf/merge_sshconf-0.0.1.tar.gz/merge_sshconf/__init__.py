# Copyright (c) 2018 Xiaoyong Guo

import json
import logging
import os
import pathlib
import sshconf


def to_list(value):
    if not isinstance(value, (list, tuple)):
        return [value]
    else:
        return value


def get_all_files(root, pattern):
    root = pathlib.Path(root).expanduser()
    return [path for path in root.rglob(pattern) if path.is_file()]


def process_identity_file(value, root):
    value = [os.path.join(root, val) for val in to_list(value)]
    for val in value:
        if not os.path.isfile(val):
            logging.warning('Identity file does not exist: %s' % value)
    return value


def process_proxy_command(value, root):
    token_list = value.split()
    for idx, token in enumerate(token_list.copy()):
        if token == '-i':
            id_file = token_list[idx+1]
            token_list[idx+1] = os.path.join(root, id_file)
    return ' '.join(token_list)


def update_host_config_path(host_config, root=None):
    root = os.path.expanduser(root or '')
    new_host_config = {}
    for key, value in host_config.items():
        if key.lower() == 'identityfile':
            value = process_identity_file(value, root)
        elif key.lower() == 'proxycommand':
            value = process_proxy_command(value, root)
        new_host_config[key] = value
    return new_host_config


def load_text(path, readlines=False):
    text_file = pathlib.Path(path).expanduser().absolute()
    if not text_file.is_file():
        content = [] if readlines else ''
    elif readlines:
        with text_file.open() as infile:
            content = infile.readlines()
    else:
        content = text_file.read_text()
    return content


DEFAULT_PROGRAM_CONFIG = '~/.ssh/merge_config.json'
DEFAULT_SSH_CONFIG = '~/.ssh/default_sshconfig'


def main():
    config_str = load_text(DEFAULT_PROGRAM_CONFIG)
    if not config_str:
        logging.error(
            'Program config file %s does not exist!', DEFAULT_PROGRAM_CONFIG)
        return

    config = json.loads(config_str)
    new_ssh_config = sshconf.empty_ssh_config()
    default_ssh_config = load_text(DEFAULT_SSH_CONFIG, readlines=True)
    if not default_ssh_config:
        logging.warning(
            f'Default ssh config {DEFAULT_SSH_CONFIG} does not exist!')

    ssh_config = sshconf.SshConfig(default_ssh_config)
    for host in ssh_config.hosts():
        host_config = ssh_config.host(host)
        host_config = update_host_config_path(host_config, root=None)
        new_ssh_config.add(host, **host_config)

    for root, each_config in config.items():
        if isinstance(each_config, dict):
            pattern = each_config['pattern']
        elif isinstance(each_config, str):
            pattern = each_config
        else:
            raise RuntimeError('Invalid pattern params!')

        for sshconf_file in get_all_files(root, pattern):
            with sshconf_file.open() as infile:
                ssh_config = sshconf.SshConfig(infile.readlines())

            for host in ssh_config.hosts():
                if host in new_ssh_config.hosts():
                  continue

                host_config = ssh_config.host(host)
                host_config = update_host_config_path(host_config, root)
                new_ssh_config.add(host, **host_config)
    print(new_ssh_config.config())


if __name__ == '__main__':
    logging.basicConfig(
        level='DEBUG',
        format='%(levelname)8s %(asctime)s %(name)s] %(message)s')
    main()
