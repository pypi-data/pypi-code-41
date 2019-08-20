from pype import __config__
import yaml
import os
import sys
from io import StringIO
import tarfile
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

def add_parser(subparsers, module_name):
    return subparsers.add_parser(module_name,
                                 help=('Management '
                                       'of pype modules'),
                                 add_help=False)


def repos_args(parser, subparsers, argv):
    lastparsers = parser.add_subparsers(dest='repos')
    parser.add_argument('-r', '--repo', dest='repo_list',
                        default=__config__.PYPE_REPOS,
                        help='Repository list. Default: %s' %
                        __config__.PYPE_REPOS)
    lastparsers.add_parser('list', add_help=False,
                           help='List the available repositories')
    lastparsers.add_parser('install', add_help=False,
                           help='Install modules from selected repository')
    # lastparsers.add_parser('sync', add_help=False,
    #                        help=('Update the installed modules to the '
    #                              'latest version in the repo'))
    lastparsers.add_parser('clean', add_help=False,
                           help=('Cleanup all module folders'))
    lastparsers.add_parser('info', add_help=False,
                           help=('Print location of the modules '
                                 'currently in use'))
    args, extra = parser.parse_known_args(argv)
    if args.repos == 'list':
        list_repos(args.repo_list)
    elif args.repos == 'install':
        install(lastparsers, extra, args.repo_list, __config__)
    elif args.repos == 'info':
        info(__config__)
    elif args.repos == 'clean':
        cleanup_dirs(lastparsers, extra, __config__)


def repos(parser, subparsers, module_name, argv, profile):
    args = repos_args(add_parser(subparsers, module_name),
                      subparsers, argv)
    return args


def load_repos(repo_list):
    with open(repo_list, 'rt') as repo_yaml:
        repo = yaml.safe_load(repo_yaml)
    return repo


def list_repos(repo_list):
    repo = load_repos(repo_list)
    for rec in repo['repositories']:
        bullet = '-'
        print('%s %s\n\t%s\n\thomepage: %s\n\tsource: %s' % (
            bullet, rec['name'], rec['description'],
            rec['homepage'], rec['source']))


def info(config):
    paths = config_paths(config)
    print_info('Profiles', paths['profiles'], 'PYPE_PROFILES')
    print_info('Pipelines', paths['pipelines'], 'PYPE_PIPELINES')
    print_info('Snippets', paths['snippets'], 'PYPE_SNIPPETS')
    print_info('Queues', paths['queues'], 'PYPE_QUEUES')


def print_info(mod_name, mod_path, env_module):
    greencol = '\033[92m'
    redcol = '\033[91m'
    endcol = '\033[0m'
    print(('- %s\n\t* modules path in use: %s%s%s\n'
           '\t tip: Adjust the env. variable %s%s%s for'
           ' a different module path') % (
        mod_name, greencol, os.path.abspath(mod_path),
        endcol, redcol, env_module, endcol))


def config_paths(config):
    modules_dirs = {'profiles': config.PYPE_PROFILES.__path__[0],
                    'pipelines': config.PYPE_PIPELINES.__path__[0],
                    'queues': config.PYPE_QUEUES.__path__[0],
                    'snippets': config.PYPE_SNIPPETS.__path__[0]}
    return modules_dirs


def install(parser, extra, repo_list, config):
    subparser = parser.add_parser('install', add_help=False)
    subparser.add_argument('name', help='Repository name to be installed')
    subparser.add_argument('-f', '--force', dest='force', action='store_true',
                           help='Overwrite files if present')
    args = subparser.parse_args(extra)
    repo_meta = None
    repo = load_repos(repo_list)
    for rec in repo['repositories']:
        if rec['name'] == args.name:
            repo_meta = rec
    if repo_meta is None:
        print ('The repository %s is not in the repository list' % args.name)
        sys.exit()
    modules_paths = config_paths(config)
    source = download_tar_archive(repo_meta['source'])
    install_tar_archive(source, modules_paths, args.force)


def download_tar_archive(url):
    print('Downloading source at %s' % url)
    response = urlopen(url)
    results = tarfile.open(fileobj=StringIO(response.read()))
    print('Source downloaded')
    return results


def install_tar_archive(tar, paths, force):
    for element in tar.getmembers():
        base, file_source = os.path.split(element.name)
        root, module = os.path.split(base)
        if module in paths.keys():
            outfile = os.path.join(paths[module], file_source)
            if force is True:
                write = True
            else:
                if os.path.isfile(outfile):
                    write = False
                else:
                    write = True
            if write is True:
                with open(outfile, 'wt') as install_file:
                    print('Installing source %s into file %s' % (
                        element.name, outfile))
                    for content in tar.extractfile(element):
                        install_file.write(content)
            else:
                print(('Skip installation of %s, '
                       'file already exists') % element.name)
    print('Installation completed')


def cleanup_dirs(parser, extra, config):
    subparser = parser.add_parser('clean', add_help=False)
    subparser.add_argument('-y', '--yes', dest='yes', action='store_true',
                           help=('Imply yes, avoiding all '
                                 'interactive questions'))
    args = subparser.parse_args(extra)
    answered = args.yes
    paths = config_paths(config)
    question = ('Do you really want to delete '
                'all files %s? (Y/N)') % ', '.join(paths.values())
    while answered is False:
        print(question)
        answer = raw_input('--> ')
        if answer == 'Y':
            answered = True
        elif answer == 'N':
            answered = True
            print('Stop cleaning process')
            sys.exit()
    for module in paths.keys():
        print('Deleting file in folder %s' % paths[module])
        path = paths[module]
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
