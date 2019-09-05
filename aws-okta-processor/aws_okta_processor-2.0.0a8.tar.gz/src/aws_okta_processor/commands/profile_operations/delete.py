from __future__ import print_function

from .base import Base

from aws_okta_processor.core import profile


class Delete(Base):
    """
    Usage:
      delete --name=<profile_name>

    Options:
      -n <profile_name> --name=<profile_name>  Name to store profile under.
    """  # noqa

    def execute(self):
        profile.delete(
            name=self.options["--name"]
        )
