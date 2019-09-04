import jmpr
import sys
import logging
import argparse


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--identity_account_id", help="Identity account ID", type=int)
    parser.add_argument("-o", "--org_unit_id", help="Organization Org Unit containing accounts")
    parser.add_argument("-r", "--shared_role", help="Shared role for accounts")
    parser.add_argument("-y", "--yaml_file", help="YAML file with complete configuration, see (future) doc")
    args = parser.parse_args()

    # Try the file style first
    parm_style = 'org_style'  # default
    if args.yaml_file:
        parm_style = "yaml_style"
        cloud_assets = jmpr.CloudAssets.from_yaml(args.yaml_file)
        # try: #wrapper for overall execution
        #     cloud_assets = CloudAssets.from_yaml(args.yaml_file)
        # except Exception as e:
        #     logging.error("An exception of type {0} occurred. Arguments:\n{1!r}".format(type(e).__name__, e.args))
        #     try:
        #         cloud_assets.print_actions()
        #         print("\nConcerns:")
        #         if len(cloud_assets.concerns) > 0:
        #             print(*cloud_assets.concerns, sep="\n")
        #         else:
        #             print("None")
        #
        #     except Exception as e:
        #         sys.exit("Exception occurred before cloud assets was defined, so no further reporting")

    elif args.org_unit_id:
        parm_style = "org_style"
        if args.identity_account_id is None:
            sys.exit("You need to supply --identity (your identity account ID)")
        if args.org_unit_id is None:
            sys.exit("You need to supply --org_unit_id when defaulting to accounts in an organization")
        if args.shared_role is None:
            sys.exit("You need to supply --shared_role when defaulting to accounts in an organization")
        cloud_assets = jmpr.CloudAssets.from_org(
            str(args.identity_account_id),
            args.org_unit_id,
            args.shared_role,
            args
        )
    else:
        sys.exit("Account list style not yet implemented")

    # Show what we have done
    print("Switches:")
    print(*cloud_assets.switches, sep="\n")

    print("\nConcerns:")
    if len(cloud_assets.concerns) > 0:
        print(*cloud_assets.concerns, sep="\n")
    else:
        print("None")

    print("\nPrincipals:")
    for principal in cloud_assets.principals:
        if principal.path == principal.desired_path:
            print(principal.path + principal.username + ' is ' + principal.arn)
        else:
            print(principal.path + principal.username + ' path changed to ' + principal.arn)
        try:
            print("Initial password is {}".format(principal.initial_pass))
        except Exception as e:
            pass
        principal.print_switchroles()

    print("\nAcquired target accounts and roles:")
    for account in cloud_assets.target_accounts.values():
        print("%s (%s)" % (account.id, account.name))
        for role in account.target_roles.values():
            if "Arn" not in role:
                print(
                    "- FAILED ACTION ON ACCOUNT {} and ROLE {}{}, see errors".
                    format(account.id, role["Path"], role["RoleName"])
                )
            else:
                print("-  " + role["Path"] + role["RoleName"] + '=' + role["Arn"])

    cloud_assets.print_actions()


if __name__ == "__main__":
    main()
