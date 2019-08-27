from argparse import ArgumentParser, RawTextHelpFormatter


def get_args_parser():
    route_sync_instruction = "\nTo perform route sync operation:" \
                             "\n 1. Test routing in Sandbox `vgs --tenant=tnt_sandbox route --dump-all > my-route-file.yaml` After this edit `my-route-file.yaml` as you need" \
                             "\n 2. Update your routes `vgs --tenant=tnt123 route --sync-all < my-route-file.yaml`" \
                             "\n 3. Promote your routes to Live `vgs --tenant=tnt_live route --sync-all < my-route-file.yaml`"

    _parser = ArgumentParser(add_help=True, description='VGS Client', formatter_class=RawTextHelpFormatter)

    _parser.add_argument('-t', '--tenant', help='Your VGS Vault\'s Tenant Identifier. E.g. tnt123abc (Required)')
    _parser.add_argument('-e', '--environment', help='VGS environment: sandbox, live, dev (Optional, default: sandbox)', default='sandbox')
    _parser.add_argument('-d', '--debug', default=False, action='store_true', dest="debug", help='Flag to run in debug mode')

    subparsers = _parser.add_subparsers(help='sub-command help', dest='subparser_name')

    subparsers.add_parser('authenticate', help='Establish an authenticated session')
    subparsers.add_parser('logout', help='Remove an authenticated session')
    subparsers.add_parser('version', help='Show current installed version')

    route_parser = subparsers.add_parser('route', help='Perform operation with VGS routes (dump, sync) %s' % route_sync_instruction)

    route_parser.add_argument('--dump-all', default=False, action='store_true', help='Dump all routes to a file or stdout')
    route_parser.add_argument('--sync-all', default=False, action='store_true', help='Sync all routes from a file or stdin')

    return _parser
