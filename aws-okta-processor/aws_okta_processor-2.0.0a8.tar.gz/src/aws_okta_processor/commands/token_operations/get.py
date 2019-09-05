"""The token_operations command."""

from __future__ import print_function

import os
import json

from .base import Base
from aws_okta_processor.core.fetcher import SAMLFetcher
from botocore.credentials import JSONFileCache


UNIX_EXPORT_STRING = ("export AWS_ACCESS_KEY_ID='{}' && "
                      "export AWS_SECRET_ACCESS_KEY='{}' && "
                      "export AWS_SESSION_TOKEN='{}'")

NT_EXPORT_STRING = ("$env:AWS_ACCESS_KEY_ID='{}'; "
                    "$env:AWS_SECRET_ACCESS_KEY='{}'; "
                    "$env:AWS_SESSION_TOKEN='{}'")


class Get(Base):
    """
    Usage:
      get [--environment] [--organization=<okta_organization>]
          [--user=<user_name>] [--pass=<user_pass>]
          [--application=<okta_application>]
          [--role=<role_name>]
          [--duration=<duration_seconds>]
          [--key=<key>]
          [--factor=<factor>]
          [--silent]
          
    Options:
      -e --environment                                           Dump auth into ENV variables.
      -u <user_name> --user=<user_name>                          Okta user name.
      -p <user_pass> --pass=<user_pass>                          Okta user password.
      -o <okta_organization> --organization=<okta_organization>  Okta organization domain.
      -a <okta_application> --application=<okta_application>     Okta application url.
      -r <role_name> --role=<role_name>                          AWS role ARN.
      -d <duration_seconds> --duration=<duration_seconds>        Duration of role session [default: 3600].
      -k <key> --key=<key>                                       Key used for generating and accessing cache.
      -f <factor> --factor=<factor>                              Factor type for MFA.
      -s --silent                                                Run silently.
    """  # noqa

    def execute(self):
        cache = JSONFileCache()
        saml_fetcher = SAMLFetcher(
            self,
            cache=cache
        )

        credentials = saml_fetcher.fetch_credentials()

        if self.args["AWS_OKTA_ENVIRONMENT"]:
            if os.name == 'nt':
                print(NT_EXPORT_STRING.format(
                    credentials["AccessKeyId"],
                    credentials["SecretAccessKey"],
                    credentials["SessionToken"]
                ))
            else:
                print(UNIX_EXPORT_STRING.format(
                    credentials["AccessKeyId"],
                    credentials["SecretAccessKey"],
                    credentials["SessionToken"]
                ))
        else:
            credentials["Version"] = 1
            print(json.dumps(credentials))

    def get_pass(self):
        if self.args["AWS_OKTA_PASS"]:
            return self.args["AWS_OKTA_PASS"]
