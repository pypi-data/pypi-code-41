# -*- coding: utf-8 -*-

import os


def read_requirements(file_dir, name=None):
    def remove_comments(file_obj):
        return [r.strip() for r in file_obj.readlines() if len(r.strip()) > 0 and r.strip()[0] != '#']

    name = 'requirements.txt' if name is None else '{}-requirements.txt'.format(name)
    file_path = os.path.join(file_dir, name)
    with open(file_path) as f:
        return remove_comments(f)
