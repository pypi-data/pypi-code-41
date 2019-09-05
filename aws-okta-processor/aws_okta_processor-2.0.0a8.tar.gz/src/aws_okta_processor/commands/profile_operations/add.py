"""The token_operations command."""

from __future__ import print_function

from .base import Base

from aws_okta_processor.core.fetcher import ClientInput

from aws_okta_processor.core import profile


class Add(Base):
    """
    Usage:
      add --organization=<okta_organization> --user=<user_name> --name=<profile_name>
             [--pass=<user_pass>]
             [--duration=<duration_seconds>]
             [--silent]
             [--nt]

    Options:
      -u <user_name> --user=<user_name>                          Okta user name.
      -p <user_pass> --pass=<user_pass>                          Okta user password.
      -o <okta_organization> --organization=<okta_organization>  Okta organization domain.
      -d <duration_seconds> --duration=<duration_seconds>        Duration of role session [default: 3600].
      -n <profile_name> --name=<profile_name>                    Name to store profile under.
      -s --silent                                                Run silently.
      --nt                                                       Use aws-okta-processor.cmd.                                         
    """  # noqa

    def execute(self):
        profile_name = self.options["--name"]

        if not profile.exits(name=profile_name):
            ClientInput(self)

            profile.add(
                name=profile_name,
                args=self.args,
                options=self.options
            )

    def get_pass(self):
        if self.args["AWS_OKTA_PASS"]:
            return self.args["AWS_OKTA_PASS"]
