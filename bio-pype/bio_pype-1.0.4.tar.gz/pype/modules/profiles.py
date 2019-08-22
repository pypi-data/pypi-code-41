from pype.utils.profiles import get_profiles, check_profile_files, \
    check_programs_env_module, check_programs_path, print_checks


def add_parser(subparsers, module_name):
    return subparsers.add_parser(module_name,
                                 help=('Set of databases softwares '
                                       'and meta information'),
                                 add_help=False)


def profiles_args(parser, subparsers, argv):
    lastparsers = parser.add_subparsers(dest='profile')
    lastparsers.add_parser('info', add_help=False,
                           help='Retrieve details from available profiles')
    lastparsers.add_parser('check', add_help=False,
                           help='Check if a profile is valid')
    args, extra = parser.parse_known_args(argv)
    profiles = get_profiles({})
    if args.profile == 'info':
        info_profiles(lastparsers, profiles, extra)
    elif args.profile == 'check':
        check_profiles(lastparsers, profiles, extra)


def profiles(parser, subparsers, module_name, argv, profile):
    args = profiles_args(add_parser(subparsers, module_name),
                         subparsers, argv)
    return args


def check_profiles(parser, profiles, argv):
    subparser = parser.add_parser('check', add_help=False)
    subparser.add_argument('name', action='store', choices=profiles.keys(),
                           help='Name of profile to check')
    subparser.add_argument('-f', '--files', dest='files',
                           action='store_true',
                           help='Check only the Profile files')
    subparser.add_argument('-p', '--programs', dest='programs',
                           action='store_true',
                           help='Check only the Profile programs')
    args = subparser.parse_args(argv)
    profile = profiles[args.name]
    if args.files == args.programs:
        files = True
        programs = True
    else:
        files = args.files
        programs = args.programs
    if files is True:
        files_check = check_profile_files(profiles[args.name])
        print_checks(files_check, profile.files)
    if programs is True:
        try:
            programs_load = profile.programs_load
        except AttributeError:
            programs_load = 'path'
        if programs_load == 'env_modules':
            programs_check = check_programs_env_module(profile)
            print_checks(programs_check, profile.programs, True)
        else:
            programs_check = check_programs_path(profile)
            print_checks(programs_check, profile.programs, False)


def info_profiles(parser, profiles, argv):
    subparser = parser.add_parser('info', add_help=False)
    subparser.add_argument('-p', '--profile', dest='profile',
                           action='store', choices=profiles.keys(),
                           help='Print details of a seleced profile')
    subparser.add_argument('-a', '--all', dest='all', action='store_true',
                           help='List all profiles')
    args, extra = subparser.parse_known_args(argv)
    if args.all:
        for profile in profiles:
            print('%s:\t%s' % (profile, profiles[profile].info['description']))
    elif args.profile:
        used_profile = args.profile
        if used_profile in profiles.keys():
            profiles[used_profile].describe()
    else:
        return subparser.print_help()
