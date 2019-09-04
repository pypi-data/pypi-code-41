import boto3
import datetime
import json
import yaml  # Uses PyYAML library
import copy
import sys
import logging
import re
import random
import string
from collections import defaultdict
import time
from jmpr import policies


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception, actions taken follow", exc_info=(exc_type, exc_value, exc_traceback))
    time.sleep(5)
    CloudAssets.print_actions()


sys.excepthook = handle_exception

logging.basicConfig(
    format='Line %(lineno)s  %(asctime)s %(levelname)s:%(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)

actions = defaultdict(list)


def dict_to_json(dict):
    policydoc = json.dumps(dict)
    return policydoc


class User:

    def __init__(
        self,
        username: str,
        arn: str,
        identity_account_creds: dict,
        identity_account_id: str = None,
        create_date: datetime = None,
        path: str = '/',
        desired_path: str = None,
        create_console_password: bool = True,
        is_prototype=False,
        config_policies: list = None,
        cloud: str = "AWS",
        enforce_mfa: bool = True,
        self_service: bool = True,
    ):
        self.path = path
        self.desired_path = desired_path
        self.username = username
        self.arn = arn
        self.create_date = create_date
        self.config_policies = config_policies
        self.is_prototype = is_prototype
        self.identity_account_creds = identity_account_creds
        self.identity_account_id = identity_account_id
        self.extend_switch_roles = []
        self.enforce_mfa = enforce_mfa
        self.self_service = self_service
        self.policy_generator = policies.Generator(identity_account_id, username, path)

    # Class and static methods
    @classmethod
    def get_iam_client(cls, identity_account_creds: dict):
        cls.iam_client = boto3.client(
            'iam',
            aws_access_key_id=identity_account_creds['AccessKeyId'],
            aws_secret_access_key=identity_account_creds['SecretAccessKey'],
            aws_session_token=identity_account_creds['SessionToken'],
        )

    @classmethod
    def from_yaml(
        cls,
        userdict: dict,
        identity_account_id: str,
        identity_account_creds: dict,
        asset_path: str = "jmpr"
    ):
        cls.get_iam_client(identity_account_creds=identity_account_creds)
        username = userdict["name"]
        if "additional_path" in userdict:
            additional_path = userdict["additional_path"]
        else:
            additional_path = ""

        if 'enforce_mfa' in userdict:
            enforce_mfa = userdict['enforce_mfa']
        else:
            enforce_mfa = True

        if 'self_service' in userdict:
            self_service = userdict['self_service']
        else:
            self_service = True

        desired_path = cls.format_path(asset_path=asset_path, additional_path=additional_path)

        aws_user = cls.get_aws_user(username=username)
        if aws_user is None:  # No user by that name
            aws_user = cls.construct_user_prototype(
                username=username,
                identity_account_id=identity_account_id,
                desired_path=desired_path
            )
            is_prototype = True
        else:
            is_prototype = False

        existing_inline_jmpr_roles = []
        existing_policies = {}

        if is_prototype is False:
            policies_to_check = ['jmpr_assume_role', 'jmpr_MFA_enforce', 'jmpr_self_service']

            for policy in policies_to_check:
                existing_policies[policy] = {}

                try:
                    result = cls.iam_client.get_user_policy(
                        UserName=aws_user["UserName"],
                        PolicyName=policy
                    )
                    existing_policies[policy] = result["PolicyDocument"]
                except cls.iam_client.exceptions.NoSuchEntityException as e:
                    logging.info(" No existing %s policy found for %s" % (policy, aws_user["UserName"]))

            if existing_policies['jmpr_assume_role'] is not {}:
                existing_inline_jmpr_roles = existing_policies['jmpr_assume_role']["Statement"][0]["Resource"]

        user = cls.from_iam_dict(
            iam_dict=aws_user,
            identity_account_creds=identity_account_creds,
            desired_path=desired_path,
            is_prototype=is_prototype
        )
        # Decorate
        user.target_roles = cls.construct_role_list(userdict["target_roles"], path=asset_path)
        user.inline_jmpr_policy = user.inline_policy_from_roles(user.target_roles)
        user.existing_inline_jmpr_roles = existing_inline_jmpr_roles
        user.existing_policies = existing_policies
        user.identity_account_id = identity_account_id
        user.policy_generator = policies.Generator(user.identity_account_id, user.username, user.path)
        user.enforce_mfa = enforce_mfa
        user.self_service = self_service

        return user

    @staticmethod
    def format_path(asset_path: str, additional_path: str):
        asset_parts = (asset_path + "/" + additional_path).split('/')
        asset_str = '/'
        for part in asset_parts:
            if part == '':
                continue
            asset_str = asset_str + part + '/'
        return asset_str

    @classmethod
    def from_iam_dict(cls, iam_dict: dict, identity_account_creds: dict, desired_path: str = None,
                      is_prototype: bool = False, enforce_mfa: bool = True, self_service: bool = True):
        cls.get_iam_client(identity_account_creds=identity_account_creds)
        user = cls(
            path=iam_dict["Path"],
            desired_path=desired_path,
            identity_account_creds=identity_account_creds,
            username=iam_dict["UserName"],
            arn=iam_dict["Arn"],
            create_date=iam_dict["CreateDate"],
            is_prototype=is_prototype,
            enforce_mfa=enforce_mfa,
            self_service=self_service
        )
        return user

    @classmethod
    def get_aws_user(cls, username: str):
        # Take a yaml/json config user and fetch corresponding aws user
        try:
            aws_user = cls.iam_client.get_user(UserName=username)
        except cls.iam_client.exceptions.NoSuchEntityException as e:
            logging.info("No user named %s, create a prototype" % username)
            return None
        return aws_user["User"]

    @staticmethod
    def randomPassword():
        """Generate a random password """
        randomSource = string.ascii_letters + string.digits + string.punctuation
        password = random.choice(string.ascii_lowercase)
        password += random.choice(string.ascii_uppercase)
        password += random.choice(string.digits)
        password += random.choice(string.punctuation)

        for i in range(12):
            password += random.choice(randomSource)

        passwordList = list(password)
        random.SystemRandom().shuffle(passwordList)
        password = ''.join(passwordList)
        return password

    @classmethod
    def inline_policy_from_roles(cls, roles):
        inline_policy = cls.blank_principal_assumerole_policy()
        for role in roles:
            inline_policy["Statement"][0]["Resource"].append(role)
        return inline_policy

    @staticmethod
    def construct_role_list(target_roles: list, path: str):
        target_arns = []
        for target in target_roles:
            role_arn = "arn:aws:iam::%s:role/%s/%s" % (target["account"], path, target["role_name"])
            target_arns.append(role_arn)
        return target_arns

    @staticmethod
    def construct_user_prototype(
        username: str,
        identity_account_id: str,
        desired_path: str,
        enforce_mfa: bool = True,
        self_service: bool = True
    ):
        predicted_arn = 'arn:aws:iam::{account}:user{path}{user}'.format(
            account=identity_account_id,
            path=desired_path,
            user=username
        )
        prototype = {
            "Path": desired_path,
            "UserName": username,
            "UserId": None,
            "Arn": predicted_arn,
            "CreateDate": None
        }
        return prototype

    @staticmethod
    def blank_principal_assumerole_policy():
        assume_role_policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Action': 'sts:AssumeRole',
                    'Resource': []
                }
            ]
        }

        return assume_role_policy

    # Instance methods
    def print_switchroles(self):
        print("\nExtend SwitchRoles plugin config:\n---------------------------------")
        print(*self.extend_switch_roles, sep="\n")
        print("=================================\n")

    def commit_principal(self):
        if self.is_prototype:  # New User
            try:
                response = self.iam_client.create_user(
                    Path=self.path,
                    UserName=self.username,
                    # PermissionsBoundary='string',
                    Tags=[
                        {
                            'Key': 'MANAGED_BY',
                            'Value': 'jmpr'
                        },
                    ]
                )
                aws_user = response["User"]
                self.arn = aws_user["Arn"]
                actions["CREATED"].append("{object},{reason}".format(object=aws_user["UserName"],
                                                                     reason="Created new user"))
                # Set initial creds
                initial_pass = self.randomPassword()
                response = self.iam_client.create_login_profile(
                    UserName=self.username,
                    Password=initial_pass,
                    PasswordResetRequired=True
                )
                iam_waiter = self.iam_client.get_waiter('user_exists')
                iam_waiter.wait(
                    UserName=self.username,
                    WaiterConfig={
                        'Delay': 20,
                        'MaxAttempts': 3
                    }
                )

                self.initial_pass = initial_pass
                actions["UPDATED"].append(
                    "{object},{reason}".format(
                        object=aws_user["UserName"],
                        reason="Initial creds set to {}".format(initial_pass)
                    )
                )
                user = self.iam_client.get_user(UserName=self.username)

            except Exception as e:
                logging.error("Commit of user %s failed with exception %s" % (self.username, e))
                actions["FAILED"].append(
                    "{object},{reason}".format(
                        object=aws_user["UserName"],
                        reason="Failed create with message " + response["ResponseMetaData]"]
                    )
                )
                return response["ResponseMetadata"]

            # CRITICAL: eventual consistency requires waiting until user fully exists before accessing from a role.
            #           Oddly the wait only works per user, not after all the users are done
            time.sleep(15)

        else:  # If existing, fix up the path
            if self.path != self.desired_path:
                response = self.iam_client.update_user(
                    UserName=self.username,
                    NewPath=self.desired_path
                )
                logging.info("Adopted and updated user {} from path {} to {}".format(
                    self.username,
                    self.path,
                    self.desired_path
                ))
                actions["UPDATED"].append("{object},{reason}".format(object=self.username,
                                                                     reason="Updated path from {} to {}".format(
                                                                         self.path, self.desired_path)))
                time.sleep(5)  # Path updates require wait for eventual consistency too
                response = self.iam_client.get_user(
                    UserName=self.username,
                )
                self.arn = response["User"]["Arn"]

        if self.self_service is False and self.enforce_mfa is True:
            logging.warning(
                'Self service is disabled and MFA is enforced for ' + self.username + ' this may cause user lockout'
            )

        # CREATE SELF SERVICE POLICY
        self_service_policy = self.policy_generator.self_service_policy()

        if 'jmpr_self_service' in self.existing_policies:
            self_service_diff = self.policy_generator.policyDiff(
                self_service_policy,
                self.existing_policies['jmpr_self_service']
            )
        else:
            self_service_diff = True

        if self_service_diff is True and self.self_service:
            try:
                policy_document_json = dict_to_json(self_service_policy)
                response = self.iam_client.put_user_policy(
                    UserName=self.username,
                    PolicyName="jmpr_self_service",
                    PolicyDocument=policy_document_json
                )
                actions["UPDATED"].append(
                    "{object},{reason}".format(object=self.username, reason="Updated self service policy document"))

            except Exception as e:
                logging.error("Failed to put self service policy for " % self.username)
                return None

        if self.self_service is False:
            logging.warning('Self Service is not enabled for ' + self.username)

            if self.existing_policies['jmpr_self_service']:
                response = self.iam_client.delete_user_policy(
                    UserName=self.username,
                    PolicyName='jmpr_self_service'
                )
                actions["DELETED"].append(
                    "{object},{reason}".format(
                        object=self.username,
                        reason="Deleted self service policy document"
                    )
                )

        # CREATE MFA ENFORCE POLICY
        mfa_enforce_policy = self.policy_generator.enforceMFA(self.enforce_mfa)

        if 'jmpr_MFA_enforce' in self.existing_policies:
            mfa_diff = self.policy_generator.policyDiff(mfa_enforce_policy, self.existing_policies['jmpr_MFA_enforce'])
        else:
            mfa_diff = True

        if mfa_diff is True and self.enforce_mfa:
            try:
                policy_document_json = dict_to_json(mfa_enforce_policy)
                response = self.iam_client.put_user_policy(
                    UserName=self.username,
                    PolicyName="jmpr_MFA_enforce",
                    PolicyDocument=policy_document_json
                )
                actions["UPDATED"].append(
                    "{object},{reason}".format(object=self.username, reason="Updated MFA policy document"))

            except Exception as e:
                logging.error("Failed to put MFA policy for " % self.username)
                return None

        if self.enforce_mfa is False:
            logging.warning('MFA is not enforced for ' + self.username)

            if self.existing_policies['jmpr_MFA_enforce']:
                response = self.iam_client.delete_user_policy(
                    UserName=self.username,
                    PolicyName='jmpr_MFA_enforce'
                )
                actions["DELETED"].append(
                    "{object},{reason}".format(object=self.username, reason="Deleted MFA policy document"))

        # Now the assume role policy
        # skip if existing user and current user policy is same as target policy
        if self.is_prototype is False:
            current_roles = self.inline_jmpr_policy["Statement"][0]["Resource"]
            inline_policy_changes = list(
                set(current_roles).symmetric_difference(
                    set(self.existing_inline_jmpr_roles)
                )
            )
            if inline_policy_changes == []:
                actions["SKIPPED"].append(
                    "{object},{reason}".format(
                        object=self.username,
                        reason="No changes in assume role policies {}".format(
                            current_roles
                        )
                    )
                )
                return  # No policy changes

        # Have assume role policy changes to persist
        self.inline_jmpr_policy["Statement"][0]["Resource"] = self.target_roles
        try:
            policy_document_json = dict_to_json(self.inline_jmpr_policy)
            response = self.iam_client.put_user_policy(
                UserName=self.username,
                PolicyName="jmpr_assume_role",
                PolicyDocument=policy_document_json
            )
            actions["UPDATED"].append(
                "{object},{reason}".format(object=self.username, reason="Updated user policy document"))

        except Exception as e:
            logging.error("User %s has malformed user policy document" % self.username)
            return None

        return response["ResponseMetadata"]


class Account:
    def __init__(self, id: str, name: str, email: str = None,
                 arn: str = None, shared_role: str = None, creds: dict = None, asset_path: str = "jmpr",
                 is_target: bool = True):
        if creds is None:  # Unsafe construction
            raise NotImplementedError('Direct instantiation of Account (%s:%s) not permitted.  '
                                      'Use Account.safe_construct classmethod' % (name, id))
        self.account_client = boto3.client(
            'iam',
            aws_access_key_id=creds['AccessKeyId'],
            aws_secret_access_key=creds['SecretAccessKey'],
            aws_session_token=creds['SessionToken']
        )
        self.id = id
        self.name = name
        self.arn = arn
        self.email = email
        self.shared_role = shared_role
        self.creds = creds
        self.source_roles = self.get_roles(asset_path=asset_path)  # gets all within path
        self.extract_role_principals(roles=self.source_roles)
        # Skip targets on identity account
        if is_target:
            self.target_roles = self.get_target_roles(self.source_roles, asset_path)
            self.new_roles = {}

    # class and static methods
    @classmethod
    def safe_construct(
        cls,
        id: str,
        name: str,
        shared_role: str,
        email: str = None,
        arn: str = None,
        creds: dict = None,
        asset_path: str = "jmpr",
        is_target: bool = True
    ):
        # Safe constructor - return existing account or None
        safe_name = name.replace(' ', '_')  # Some calls do not allow spaces
        creds = cls.acquire_creds(id, safe_name, shared_role)
        if creds is not None:
            return Account(
                id=id,
                name=name,
                email=email,
                arn=arn,
                shared_role=shared_role,
                creds=creds,
                asset_path=asset_path,
                is_target=is_target
            )
        else:
            return None

    @classmethod
    def from_org_dict(cls, shared_role: str, account_dict: dict):
        return cls.safe_construct(
            id=account_dict["Id"],
            name=account_dict["Name"],
            shared_role=shared_role,
            email=account_dict["Email"],
            arn=account_dict["Arn"]
        )

    @staticmethod
    def acquire_creds(id: str, name: str, shared_role: str):
        client = boto3.client('sts')
        try:
            response = client.assume_role(
                DurationSeconds=3600,
                RoleArn='arn:aws:iam::' + id + ':role/' + shared_role,
                RoleSessionName=name
            )
        except Exception as e:
            logging.error("SKIPPING account " + name + ' ' + id + " in acquire creds: " + e.args[0])
            return None
        credentials = response['Credentials']
        return credentials

    # instance methods

    def get_roles(self, asset_path: str):
        if self.creds is None:
            return []
        role_list = self.account_client.list_roles(PathPrefix='/' + asset_path + '/')["Roles"]
        role_dict = {}
        for role in role_list:  # Format assume_principals as a list to enable comparisons and add role to dict
            assume_principals = role["AssumeRolePolicyDocument"]["Statement"][0]["Principal"]["AWS"]
            principal_list = self.to_list(assume_principals)
            role["AssumeRolePolicyDocument"]["Statement"][0]["Principal"]["AWS"] = principal_list
            role_dict.update({role["Arn"]: role})

        return role_dict

    def extract_role_principals(self, roles: dict):
        # Surfaces the principals in each role for later comparisons and action
        for item in roles.values():  # Surface principals
            item["trust_principals"] = item["AssumeRolePolicyDocument"]["Statement"][0]["Principal"]["AWS"]

    def get_target_roles(self, source_roles: dict, asset_path: str):
        target_roles = copy.deepcopy(source_roles)  # Stripped, for reworking roles
        for role in target_roles.values():
            # Ensure target roles have specifications
            role.update({'policy_arns': {}})
            role["may_delete"] = False  # start off optimistic
            role["force_refresh_principal"] = False  # allow skips unless a new principal is involved (latency issue)
            try:
                policies = self.role_spec_dict[role["RoleName"]]
                role["policy_arns"].update(policies)
            except KeyError:
                pass
                # Handled in audit
                # logging.error(
                # "Missing role policy definitions for {}, eligible for deletion".format(role["RoleName"]))
                # role["may_delete"] = True

            # Prepare AssumeRolePolicy and trust_principals
            for statement in role["AssumeRolePolicyDocument"]["Statement"]:
                statement["Principal"] = {"AWS": []}
            role["trust_principals"] = []
            role["Path"] = "/" + asset_path + "/"
        return target_roles

    def to_list(self, item):
        if type(item) == str:
            listval = []
            listval.append(item)
            return listval
        elif type(item) == list:
            return item
        else:
            raise TypeError


class CloudAssets:
    def __init__(
        self,
        identity_account_id: str,
        shared_role: str,
        asset_path: str = 'jmpr',
        default_region: str = 'us-east-1',
        switches: list = None,
        purge_accounts: set = None
    ):
        self.shared_role = shared_role
        self.purge_accounts = set() if purge_accounts is None else purge_accounts
        self.switches = [] if switches is None else switches
        self.asset_path = asset_path
        # Populate the identity account
        self.identity_account = Account.safe_construct(
            id=identity_account_id,
            name="identity",
            shared_role=self.shared_role,
            is_target=False  # Not a target account
        )
        self.concerns = []
        self.default_region = default_region

    #  Class and static Methods
    @classmethod
    def from_org(cls, identity_account_id: str, org_unit_id: str, shared_role: str, args) -> 'CloudAssets':
        shared_role = args.shared_role

        assets = cls(
            identity_account_id=identity_account_id,
            shared_role=shared_role
        )  # instantiate early, then decorate

        org_accounts = assets.get_org_accounts(org_unit_id=org_unit_id)

        # Acquire the principals
        assets.principals = assets.get_identity_userlist()

        # Acquire and populate the target accounts
        assets.target_accounts = {}
        for account_dict in org_accounts:
            account = Account.from_org_dict(shared_role=shared_role, account_dict=account_dict)
            if account is None:
                continue  # Failed account retrieval
            assets.target_accounts.update({account.id: account})

        return assets

    @classmethod
    def from_json(cls, json_config: str) -> 'CloudAssets':
        cloudassets = json.loads(json_config)
        return cls(identity_account_id=cloudassets['identity_account_id'], accounts=cloudassets['accounts'])

    @classmethod
    def from_yaml(cls, filename: str) -> 'CloudAssets':
        ff = open(filename, 'r')
        config = yaml.safe_load(ff)
        ff.close()

        identity_account_id = config["identity_account_id"]
        shared_role_name = config["shared_role_name"]
        asset_path = config["asset_path"]
        switches = config["switches"] if "switches" in config else []
        default_region = config["default_region"] if "default_region" in config else "us-east-1"

        # Get accounts that will have roles cleaned out
        try:
            account_purge_roles = config["account_purge_roles"]
            if account_purge_roles is None:
                purge_accounts = None
            else:
                purge_accounts = set()
                for account_num in account_purge_roles:
                    purge_accounts.add(str(account_num))
        except KeyError as k:  # No accounts to clean so pass
            purge_accounts = None

        assets = cls(
            identity_account_id=identity_account_id,
            shared_role=shared_role_name,
            asset_path=asset_path,
            default_region=default_region,
            switches=switches,
            purge_accounts=purge_accounts
        )  # instantiate early, then decorate

        principals = []
        account_numbers = set()  # Guaranteed unique
        assets.principal_roles = {}
        account_specs = {}

        try:
            account_specs = config["accounts"]
        except KeyError:
            logging.warning("No managed accounts provided in YAML")

        for userdict in config["users"]:  # extract target accts and create User instances
            # Add to unique set of target accts from target_roles in each user
            try:
                for role in userdict["target_roles"]:
                    account_id = role["account"]
                    account_numbers.add(account_id)
            except (KeyError, TypeError) as e:
                # No roles, skip this user
                actions["SKIPPED"].append(
                    "User {name} has no assigned roles".format(name=userdict["name"]))
                continue

            # Construct the user
            user = User.from_yaml(
                userdict=userdict,
                identity_account_id=identity_account_id,
                identity_account_creds=assets.identity_account.creds,
                asset_path=asset_path
            )

            if user is None:  # Failed validation
                continue
            for role_arn in user.target_roles:
                # parsed_role_arn = assets.parse_role_arn(role_arn)]
                assets.principal_roles.update({role_arn: user.username})

            principals.append(user)

        # Role specs
        try:
            role_spec_list = config["roles"]
        except KeyError:
            logging.warning("No role specifications provided in YAML")
            role_spec_list = []

        role_spec_dict = {}
        for role in role_spec_list:
            if role["name"] not in role_spec_dict:
                policy_arns = {}
                try:
                    for policy_arn in role["import"]:
                        policyname = policy_arn[policy_arn.rfind('/') + 1:]
                        policy_arns.update({policyname: policy_arn})
                except KeyError:
                    error = "Malformed role in YAML {}, exiting".format(role)
                    logging.error(error)
                    sys.exit(error)

                role_spec_dict.update({role["name"]: policy_arns})
            else:
                logging.error(
                    "Role {} appears in role YAML more than once, potential collision on policies".format(
                        role["name"]
                    )
                )
                sys.exit(
                    "Role {} appears in role YAML more than once, potential collision on policies".format(
                        role["name"]
                    )
                )

        Account.role_spec_dict = role_spec_dict
        CloudAssets.role_spec_dict = role_spec_dict

        # Accounts
        target_accounts = {}
        for account_num in account_numbers:
            account = Account.safe_construct(
                id=str(account_num),
                name=str("unknown"),
                shared_role=shared_role_name,
                asset_path=asset_path
            )
            if account is None:  # Skip any failed account retrievals
                logging.warning("Skipped unretrievable account %s referenced in a role" % account_num)
            else:
                target_accounts.update({account.id: account})

        assets.principals = principals
        assets.target_accounts = target_accounts
        assets.defined_accounts = account_specs

        assets.commit()
        return assets

    @classmethod
    def print_actions(cls):
        print("\nActions Taken:")
        for actiontype, acts in actions.items():
            print(actiontype, end="\n- ")
            print(*acts, sep="\n- ")

    @staticmethod
    def parse_role_arn(arn: str):
        # removed escaped colons, but raw string for slash is failing, so this will produce warns in a pytest
        reg_str = "^(?P<r_arn>[^.]*)::(?P<r_acct>[^.]*):" \
                  "(?P<r_type>[^.]*?)\/(?P<r_full_path>[^.]*)\/(?P<r_name>[^.*]*)$"  # noqa: W605
        reg_arn = re.compile(reg_str)  # removed unneeded escapes to make pytest happy

        result = reg_arn.search(arn)
        account = result.group('r_acct')
        type = result.group('r_type')
        full_path = "/" + result.group('r_full_path') + "/"
        name = result.group('r_name')
        split_path = full_path.split('/', 2)
        asset_path = split_path[1]
        org_path = split_path[2]
        return {'account_id': account, 'type': type, 'full_path': full_path,
                'asset_path': asset_path, 'org_path': org_path, 'name': name}

    @staticmethod
    def get_org_accounts(org_unit_id):
        org_client = boto3.client("organizations")  # No creds because in org account so default
        org_accounts = org_client.list_accounts_for_parent(ParentId=org_unit_id)
        return org_accounts['Accounts']

    # Helper instance methods
    def get_identity_userlist(self):
        # Call to identity account and get the appropriate identity roles, maybe by tag or name convention
        iam = boto3.client(
            'iam',
            aws_access_key_id=self.identity_account.creds['AccessKeyId'],
            aws_secret_access_key=self.identity_account.creds['SecretAccessKey'],
            aws_session_token=self.identity_account.creds['SessionToken'],
        )
        iamUsers = iam.list_users()
        userlist = []
        for user in iamUsers["Users"]:
            userlist.append(User.from_iam_dict(user, self.identity_account.creds))

        return userlist

    def commit(self):

        # 1 Update the targets, including target_account role trust policies in memory to
        #   align with principal assumeRole permissions, extend_switch_roles in principals, etc.
        self.update_targets(self.principals, self.defined_accounts)

        # 2. Audit precommit state and abort or proceed
        proceed, self.concerns = self.precommit_audit()
        if proceed is False:  # Abort
            time.sleep(1)  # Give the log a chance to finish printing
            self.abort(self.concerns)

        # 3 Remove scoped roles in accounts listed for cleaning
        self.accounts_role_clean()

        # 4 Commit each principal's inline assumeRole Policy
        for principal in self.principals:
            principal.commit_principal()

        # 5 ... commit the updated target account roles
        for target_account in self.target_accounts.values():
            self.commit_roles(target_account)

    def accounts_role_clean(self):
        if self.purge_accounts is None:
            actions["SKIPPED"].append(
                "No accounts marked for role clean")
            return
        scope_path = '/' + self.asset_path
        for account_id in self.purge_accounts:
            try:
                account = self.target_accounts[account_id]
            except KeyError as k:
                account = Account.safe_construct(
                    id=account_id,
                    name="cleanup",
                    shared_role=self.shared_role,
                    asset_path=scope_path
                )
                if account is None:
                    logging.warning(
                        "Skipping requested purge of account {} because no credentials".format(account_id)
                    )
                    actions["ERROR"].append(
                        "account {account} purge of roles in path {path} skipped because no credentials".format(
                            account=account_id,
                            path=scope_path
                        )
                    )
                    continue

            response = account.account_client.list_roles(PathPrefix=scope_path)
            for role in response["Roles"]:
                logging.info("Account {} purge of role {} in path {} ".format(
                    account.id,
                    role["RoleName"],
                    role["Path"]
                ))
                policy_resp = account.account_client.list_attached_role_policies(
                    RoleName=role["RoleName"]
                )

                for policy in policy_resp["AttachedPolicies"]:
                    account.account_client.detach_role_policy(
                        RoleName=role["RoleName"],
                        PolicyArn=policy["PolicyArn"]
                    )
                    actions["DETACHED"].append(
                        "Detached the \"{policy_arn}\" policy from role {rolename} in account {account_id} before"
                        " purging the role ".format(
                            policy_arn=policy["PolicyArn"],
                            rolename=role["RoleName"],
                            account_id=account.id
                        )
                    )
                deleted_resp = account.account_client.delete_role(RoleName=role["RoleName"])
                actions["DELETED"].append(
                    "account {account} purge of role {role} in path {path} "
                    "because purge of roles requested".format(
                        account=account.id,
                        role=role["RoleName"],
                        path=scope_path
                    )
                )

    def update_targets(self, principals, defined_accounts):
        for principal in principals:
            for role_arn in principal.target_roles:
                parsed_role_arn = self.parse_role_arn(role_arn)

                try:
                    target_account_id = parsed_role_arn["account_id"]
                    target_account = self.target_accounts[target_account_id]
                except KeyError as e:  # Missing account, likely frm prior creds fail, so skip
                    logging.warning("Continuing to skip account %s" % (parsed_role_arn["account_id"]))
                    continue

                # Use existing target role unless already prototyped or missing
                try:
                    existing_target = target_account.target_roles[role_arn]
                    if "is_prototype" in existing_target or target_account_id not in self.purge_accounts:
                        target_role = target_account.target_roles[role_arn]  # use existing
                    else:  # Create a proto and add to new
                        target_role = self.create_proto_role(parsed_role_arn, role_arn)
                        target_account.new_roles.update({role_arn: target_role})
                except KeyError as ke:  # Create a proto and add to new
                    target_role = self.create_proto_role(parsed_role_arn, role_arn)
                    target_account.new_roles.update({role_arn: target_role})
                target_account.target_roles.update({role_arn: target_role})  # Regardless

                # if target_account_id in self.purge_accounts or role_arn not in target_account.target_roles:
                #     target_role = self.create_proto_role(parsed_role_arn, role_arn, target_role)
                #
                #     target_account.target_roles.update({role_arn:target_role})
                #     target_account.new_roles.update({role_arn:target_role})
                # else: target_role = target_account.target_roles[role_arn]

                # Regardless of old or new, add the principal to the trust_principals and arp document
                target_role["trust_principals"].append(principal.arn)  # Then add the principal
                target_role["AssumeRolePolicyDocument"]["Statement"][0]["Principal"]["AWS"].append(principal.arn)

                if principal.is_prototype is True:
                    target_role["force_refresh_principal"] = True  # To deal with latency on recreate users

                # Add configuration for role switcher
                roleaccount = parsed_role_arn["account_id"]

                config_name = parsed_role_arn["account_id"] + parsed_role_arn["full_path"] + parsed_role_arn["name"]
                region = self.default_region
                color = "%06x" % random.randint(0, 0xFFFFFF)

                # LOOK FOR ACCOUNT CONFIGURATIONS
                for key in defined_accounts:
                    key_str = str(key)

                    if 'account_number' in defined_accounts[key_str]:
                        this_acct_num = str(defined_accounts[key_str]['account_number'])

                    elif key.isdigit() and len(key_str) == 12:
                        this_acct_num = key_str

                    if parsed_role_arn['account_id'] == this_acct_num:
                        matched_key = key_str
                        matched_act = defined_accounts[key_str]

                        if 'name' in matched_act.keys():
                            config_name = matched_act['name']
                        else:
                            config_name = matched_key + ' ' + parsed_role_arn["name"]

                        if 'default_region' in matched_act.keys():
                            region = matched_act['default_region']

                        if 'color' in matched_act.keys():
                            color = matched_act['color']

                principal.extend_switch_roles.append(
                    "[{}]\n"
                    "aws_account_id = {}\n"
                    "role_name = {}\n"
                    "color = {}\n"
                    "region = {}\n".format(
                        config_name,
                        parsed_role_arn['account_id'],
                        parsed_role_arn["full_path"][1:] + parsed_role_arn["name"],
                        color,
                        region
                    )
                )

    def create_proto_role(self, parsed_role_arn, role_arn):
        arp_template = {"Version": "2012-10-17",
                        "Statement": [{"Effect": "Allow", "Principal": {"AWS": []}, "Action": "sts:AssumeRole"}]}
        target_role = {
            "Path": parsed_role_arn["full_path"], "RoleName": parsed_role_arn["name"],
            "Description": "from jmpr", "AssumeRolePolicyDocument": arp_template,
            "trust_principals": [], "policy_arns": {},
            "Arn": role_arn,
            "may_delete": False,
            "force_refresh_principal": False,
            "is_prototype": True,
            "Tags": [
                {
                    'Key': 'MANAGED_BY',
                    'Value': 'jmpr'
                },
            ]
        }
        return target_role

    def commit_roles(self, target_account):
        for role_arn, role in target_account.target_roles.items():
            concern_list = self.has_concern(role_arn)
            if len(concern_list) > 0:
                for concern in concern_list:
                    print(concern[role_arn])

            if role["trust_principals"] == []:  # no principals, so flag for delete or skip according to switch
                if target_account.id in self.purge_accounts:
                    continue  # Because purged and would be deleted anyway
                role["may_delete"] = True  # Flag for delete
            else:  # Has principals so update
                #  trust role policies
                self.update_trust_principals(role, target_account)

            # Update permission role policies, even if flagged for delete
            self.update_role_policies(role, target_account)

            # Remove roles marked for deletion
            if role["may_delete"] is True:
                self.remove_tbd_roles(role, target_account)

    def remove_tbd_roles(self, role, target_account):
        if "skip-role-deletion" in self.switches:
            actions["SKIPPED"].append(
                "{account},{role},{reason}".format(
                    account=target_account.id,
                    role=role["RoleName"],
                    reason="Role marked for deletion, but skipped because skip-role-deletion switch present"
                )
            )
            return
        response = target_account.account_client.delete_role(
            RoleName=role["RoleName"])
        actions["DELETED"].append(
            "{account},{role},{reason}".format(
                account=target_account.id,
                role=role["RoleName"],
                reason="Role marked for deletion, deleting because skip-role-deletion switch absent"
            )
        )

    def update_role_policies(self, role, target_account):
        if role["may_delete"] and "skip-role-deletion" in self.switches:
            actions["SKIPPED"].append(
                "{account},{role},{reason}".format(
                    account=target_account.id,
                    role=role["RoleName"],
                    reason="Role marked for deletion, but skipping policy detach "
                           "because skip-role-deletion switch present"
                )
            )
            return

        response = target_account.account_client.list_attached_role_policies(RoleName=role["RoleName"])

        current_policies = set()
        desired_policies = set()
        attach_policies = set()

        for policy in response["AttachedPolicies"]:
            current_policies.add(policy["PolicyArn"])

        for policy_name, policy_arn in role["policy_arns"].items():
            desired_policies.add(policy_arn)

        if role["may_delete"]:  # zero out current policies
            detach_policies = current_policies  # detach all existing, leave attach_policies as empty
        else:  # compute what needs to be removed by a difference calculation
            attach_policies = desired_policies - current_policies
            detach_policies = current_policies - desired_policies

        for detach_arn in detach_policies:
            target_account.account_client.detach_role_policy(
                RoleName=role["RoleName"],
                PolicyArn=detach_arn
            )
            actions["DETACHED"].append(
                "Detaching the \"{policy_arn}\" policy from role {rolename} in account "
                "{account_id} because the policy is no longer specified for the role".
                format(policy_arn=detach_arn, rolename=role["RoleName"], account_id=target_account.id)
            )

        for attach_arn in attach_policies:
            target_account.account_client.attach_role_policy(
                RoleName=role["RoleName"],
                PolicyArn=attach_arn
            )
            actions["ATTACHED"].append(
                "Attaching the \"{policy_arn}\" policy to role {rolename} in account {account_id}".
                format(policy_arn=attach_arn, rolename=role["RoleName"], account_id=target_account.id))

    def update_trust_principals(self, role, target_account):
        role_arn = role["Arn"]
        regenerate_role = True if target_account.id in self.purge_accounts else False
        if regenerate_role is False and role_arn in target_account.source_roles:  # existing role in source
            trust_principal_changes = list(
                set(role["trust_principals"]).symmetric_difference(
                    set(target_account.source_roles[role_arn]["trust_principals"])
                )
            )
            if role["force_refresh_principal"] is True or trust_principal_changes != []:
                assume_role_policy_doc = json.dumps(role["AssumeRolePolicyDocument"])
                response = target_account.account_client.update_assume_role_policy(
                    RoleName=role["RoleName"],
                    PolicyDocument=assume_role_policy_doc)
                if role["force_refresh_principal"] is True:
                    reason = "Force updated assume role policy because of new principal"
                else:
                    reason = "Changes in principals"
                actions["UPDATED"].append(
                    "{object},{reason}".format(object=role["Arn"], reason=reason))

        else:  # New or regenerated role - takes a string ARP instead of a dict!
            arp_string = dict_to_json(role["AssumeRolePolicyDocument"])
            response = target_account.account_client.create_role(
                Path=role["Path"], RoleName=role["RoleName"],
                AssumeRolePolicyDocument=arp_string,
                Description="JMPR created role", Tags=[{'Key': 'MANAGED_BY', 'Value': 'jmpr'}, ]
            )
            logging.info(
                "Created role with assume role policy %s with response %s" % (
                    role["RoleName"],
                    response["ResponseMetadata"]["HTTPStatusCode"]
                )
            )
            actions["CREATED"].append(
                "{account},{role},{reason}".format(account=target_account.id, role=role["RoleName"],
                                                   reason="Created new role"))
            role.update(response["Role"])  # Refresh with real data including ARN
            # Add the policy ARNs for the role in the account
            role_spec_dict = target_account.role_spec_dict
            role_spec = role_spec_dict[role["RoleName"]]
            for name, arn in role_spec.items():
                role["policy_arns"][name] = arn

    def persist_role_policy(self, assume_role_policy_doc, role, target_account):
        response = target_account.account_client.update_assume_role_policy(
            RoleName=role["RoleName"],
            PolicyDocument=assume_role_policy_doc)
        actions["UPDATED"].append(
            "{object},{reason}".format(object=role["Arn"], reason="Updated assume role policy"))

    def precommit_audit(self):
        # Check things out before a commit
        # Look out for removing last trusted principal
        concerns = []
        proceed = True

        # Check for roles present in user but not specified in roles
        for principal_role, username in self.principal_roles.items():
            parsed_role = self.parse_role_arn(principal_role)
            if parsed_role["name"] not in self.role_spec_dict:
                logging.error("Role ARN {} in user {} is not specified in roles definition"
                              .format(principal_role, username))
                concerns.append({principal_role: "FATAL: Role in YAML user {} is not "
                                                 "specified in YAML roles definition".format(username)})
                proceed = False

        for account in self.target_accounts.values():
            for arn, target_role in account.target_roles.items():
                # Get convenience attributes
                role_name = target_role["RoleName"]
                account_id = account.id

                # check for role name collisions:
                if arn in account.new_roles:
                    try:
                        response = account.account_client.get_role(RoleName=target_role["RoleName"])
                        existing_path = response["Role"]["Path"]
                        # Check for collision outside of any account to be cleaned of roles
                        if account_id in self.purge_accounts and existing_path == parsed_role["full_path"]:
                            pass
                        else:  # Role not to be cleaned but still collides
                            proceed = False
                            concerns.append({arn: 'FATAL: Role %s already exists in account %s  with path %s' % (
                                role_name, account_id, response["Role"]["Path"])})

                    except account.account_client.exceptions.NoSuchEntityException as e:
                        # That's good, no role collision
                        continue

                # check over the roles, mark deletions, affirm policies exist
                try:
                    role_policies = account.role_spec_dict[role_name]
                except KeyError as e:
                    if "skip-role-deletion" in self.switches:
                        concerns.append(
                            {arn: "WARN: Role {} in account {} has no YAML policy configuration.  "
                                  "Skipping because of switch skip-role-deletion".format(role_name, account_id)})
                        target_role["may_delete"] = False
                    else:
                        concerns.append({arn: "INFO: Role {} in account {} has no YAML policy configuration."
                                        "  Mark for delete".format(role_name, account_id)})
                        target_role["may_delete"] = True
                    continue

                required_policies = set()
                available_policies = set()

                for policy in role_policies.keys():
                    required_policies.add(policy)
                searchstringlist = []
                for value in required_policies:
                    string = "PolicyName == '{}' ".format(value)
                    searchstringlist.append(string)
                searchstring = "Policies[?{}]".format(" || ".join(searchstringlist))
                paginator = account.account_client.get_paginator('list_policies')
                page_iterator = paginator.paginate(Scope='All')
                filtered_iterator = page_iterator.search(searchstring)
                for policy in filtered_iterator:
                    available_policies.add(policy["PolicyName"])
                missing_policies = required_policies - available_policies
                if len(missing_policies) > 0:
                    logging.error("Account {} missing policy {}".format(account.id, missing_policies))
                    for missing in missing_policies:
                        if "skip-missing-policies" not in self.switches:
                            proceed = False
                        severity = "WARN:" if proceed else "FATAL: "
                        concerns.append({missing: "{} Account {} missing policy {}".
                                        format(severity, account.id, missing)})
        return proceed, concerns

    def has_concern(self, arn):
        concern_list = []
        for concern in self.concerns:
            if arn in concern:
                concern_list.append(concern)

        return concern_list

    def abort(self, concerns: list):
        self.print_actions()
        print("Concerns:")
        for concern in concerns:
            for arn, message in concern.items():
                print("{}\n      -- {}".format(message, arn))
        print("Switches:")
        print(self.switches)
        sys.exit("\nAborted in audit phase, see concerns.")
