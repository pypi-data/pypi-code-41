import sys

from vgscli import _version
from vgscli.api import create_api
from vgscli.config import load_config
from vgscli.routes import dump_all_routes, sync_all_routes
from vgscli.utils import is_file_accessible, eprint
from vgscli.auth import logout, login, handshake, AuthenticateException
from vgscli.keyring_token_util import KeyringTokenUtil
from simple_rest_client import exceptions

token_util = KeyringTokenUtil()


def routes_args_defined(args):
    return [args.dump_all, args.sync_all].count(True)


def process_route(args):
    vgs_api = create_api(args.tenant, args.environment, token_util.get_access_token())
    # Dump routes operation
    if args.dump_all:
        dump = dump_all_routes(vgs_api)
        print(dump)
    # Sync routes operation
    if args.sync_all:
        dump_data = sys.stdin.read()
        updated_dump = sync_all_routes(vgs_api, dump_data, lambda route_id: eprint(f'Route {route_id} processed'))
        print(updated_dump)
        eprint(f'Routes updated successfully for tenant {args.tenant}')


def main(args):
    try:
        if args.subparser_name == 'version':
            print(_version.version())
            return

        if args.subparser_name == 'logout':
            logout()
            return

        config_file = load_config()
        if args.subparser_name == 'authenticate':
            login(config_file, args.environment)

        elif args.subparser_name == 'route':
            # Validate only one positional parameter for `route` action is present
            route_args_num = routes_args_defined(args)
            if route_args_num != 1:
                adverb = ("At least", "Only")[route_args_num < 1]
                eprint(f"{adverb} one route parameter is required (--dump-all or --sync-all)", fatal=True)
            # Validate that `tenant` is present
            if not args.tenant:
                eprint("Please specify --tenant option.", fatal=True)
            # Validate authenticate token
            handshake(config_file, args.environment)
            # Process route action
            process_route(args)

        else:
            eprint("Please provide action to run. You can view the instruction, by running `vgs --help` or `vgs -h`", fatal=True)
    except AuthenticateException as e:
        eprint(e.message, debug=args.debug, fatal=True)
    except exceptions.ClientError as e:
        eprint(f'Rest call error occurred: {e.message}', debug=args.debug, fatal=True)
    except Exception:
        eprint('An unexpected error occurred. (Run with --debug for a traceback.)', debug=args.debug, fatal=True)

