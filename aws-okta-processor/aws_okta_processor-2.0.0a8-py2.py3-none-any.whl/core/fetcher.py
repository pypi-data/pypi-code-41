import boto3
import json
import aws_okta_processor.core.saml as saml
import aws_okta_processor.core.prompt as prompt

from hashlib import sha1
from aws_okta_processor.core.okta import Okta
from botocore.credentials import CachedCredentialFetcher
from aws_okta_processor.core.print_tty import print_tty


class SAMLFetcher(CachedCredentialFetcher):
    def __init__(self, command, cache=None, expiry_window_seconds=600):
        self._command = command
        self._cache = cache
        self._stored_cache_key = None
        self._expiry_window_seconds = expiry_window_seconds

    @property
    def _cache_key(self):
        if self._stored_cache_key is None:
            self._stored_cache_key = self._create_cache_key()
        return self._stored_cache_key

    def _create_cache_key(self):
        key_dict = self._command.get_key_dict()
        key_string = json.dumps(key_dict, sort_keys=True)
        key_hash = sha1(key_string.encode()).hexdigest()
        return self._make_file_safe(key_hash)

    def fetch_credentials(self):
        credentials = super(SAMLFetcher, self).fetch_credentials()

        return {
            'AccessKeyId': credentials['access_key'],
            'SecretAccessKey': credentials['secret_key'],
            'SessionToken': credentials['token'],
            'Expiration': credentials['expiry_time']
        }

    def _get_credentials(self):
        # Do NOT load credentials from ENV or ~/.aws/credentials
        client = boto3.client(
            'sts',
            aws_access_key_id='',
            aws_secret_access_key='',
            aws_session_token=''
        )

        client_input = ClientInput(
            self._command,
            silent=True
        )

        response = client.assume_role_with_saml(
            RoleArn=client_input.aws_role.role_arn,
            PrincipalArn=client_input.aws_role.principal_arn,
            SAMLAssertion=client_input.saml_assertion,
            DurationSeconds=int(self._command.args["AWS_OKTA_DURATION"])
        )

        expiration = (response['Credentials']['Expiration']
                      .isoformat().replace("+00:00", "Z"))

        response['Credentials']['Expiration'] = expiration

        return response


class ClientInput:
    def __init__(self, command, silent=False):
        if silent:
            silent = command.args["AWS_OKTA_SILENT"]

        okta = Okta(
            user_name=command.args["AWS_OKTA_USER"],
            user_pass=command.get_pass(),
            organization=command.args["AWS_OKTA_ORGANIZATION"],
            factor=command.args["AWS_OKTA_FACTOR"],
            silent=silent
        )

        if not command.args["AWS_OKTA_APPLICATION"]:
            applications = okta.get_applications()

            command.args["AWS_OKTA_APPLICATION"] = prompt.get_item(
                items=applications,
                label="AWS application"
            )

        saml_response = okta.get_saml_response(
            application_url=command.args["AWS_OKTA_APPLICATION"]
        )

        self.saml_assertion = saml.get_saml_assertion(
            saml_response=saml_response
        )

        aws_roles = saml.get_aws_roles(
            saml_assertion=self.saml_assertion
        )

        self.aws_role = prompt.get_item(
            items=aws_roles,
            label="AWS Role",
            key=command.args["AWS_OKTA_ROLE"]
        )

        command.args["AWS_OKTA_ROLE"] = self.aws_role.role_arn

        print_tty(
            "Role: {}".format(self.aws_role.role_arn),
            silent=silent
        )
