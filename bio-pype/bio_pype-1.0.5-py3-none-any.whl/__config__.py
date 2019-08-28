import os
from pype.misc import try_import

PYPE_MODULES = os.environ.get('PYPE_MODULES')
PYPE_SNIPPETS = os.environ.get('PYPE_SNIPPETS')
PYPE_PROFILES = os.environ.get('PYPE_PROFILES')
PYPE_PIPELINES = os.environ.get('PYPE_PIPELINES')
PYPE_QUEUES = os.environ.get('PYPE_QUEUES')
PYPE_REPOS = os.environ.get('PYPE_REPOS')
PYPE_NCPU = os.environ.get('PYPE_NCPU')
PYPE_MEM = os.environ.get('PYPE_MEM')

if PYPE_MODULES:
    pype_snippets = try_import(PYPE_MODULES, 'snippets')
    pype_profiles = try_import(PYPE_MODULES, 'profiles')
    pype_pipelines = try_import(PYPE_MODULES, 'pipelines')
    pype_queues = try_import(PYPE_MODULES, 'queues')
    PYPE_SNIPPETS = pype_snippets
    PYPE_PROFILES = pype_profiles
    PYPE_PIPELINES = pype_pipelines
    PYPE_QUEUES = pype_queues
else:
    if PYPE_SNIPPETS:
        base, name = os.path.split(os.path.abspath(PYPE_SNIPPETS))
        pype_snippets = try_import(base, name)
        PYPE_SNIPPETS = pype_snippets
    else:
        base, name = os.path.split(os.path.abspath(__file__))
        pype_snippets = try_import(base, 'snippets')
        PYPE_SNIPPETS = pype_snippets

    if PYPE_PROFILES:
        base, name = os.path.split(os.path.abspath(PYPE_PROFILES))
        pype_profiles = try_import(base, name)
        PYPE_PROFILES = pype_profiles
    else:
        base, name = os.path.split(os.path.abspath(__file__))
        pype_profiles = try_import(base, 'profiles')
        PYPE_PROFILES = pype_profiles

    if PYPE_PIPELINES:
        base, name = os.path.split(os.path.abspath(PYPE_PIPELINES))
        pype_pipelines = try_import(base, name)
        PYPE_PIPELINES = pype_pipelines
    else:
        base, name = os.path.split(os.path.abspath(__file__))
        pype_pipelines = try_import(base, 'pipelines')
        PYPE_PIPELINES = pype_pipelines

    if PYPE_QUEUES:
        base, name = os.path.split(os.path.abspath(PYPE_QUEUES))
        pype_queues = try_import(base, name)
        PYPE_QUEUES = pype_queues
    else:
        base, name = os.path.split(os.path.abspath(__file__))
        pype_queues = try_import(base, 'queues')
        PYPE_QUEUES = pype_queues

if PYPE_REPOS:
    if not os.path.isfile(PYPE_REPOS):
        raise Exception('File %s does not exits' % PYPE_REPOS)
else:
    base, name = os.path.split(os.path.abspath(__file__))
    PYPE_REPOS = os.path.join(base, 'repos.yaml')
