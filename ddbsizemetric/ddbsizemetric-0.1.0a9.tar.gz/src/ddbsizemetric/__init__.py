import abc
import datetime
import enum
import typing

import jsii
import jsii.compat
import publication

from jsii.python import classproperty

import aws_cdk.aws_events
import aws_cdk.aws_events_targets
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.core
__jsii_assembly__ = jsii.JSIIAssembly.load("@richardhboyd/ddbsizemetric", "0.1.0-alpha.9", __name__, "ddbsizemetric@0.1.0-alpha.9.jsii.tgz")
class DDBSizeLib(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@richardhboyd/ddbsizemetric.DDBSizeLib"):
    def __init__(self, scope: aws_cdk.core.Construct, id: str) -> None:
        """
        :param scope: -
        :param id: -
        """
        jsii.create(DDBSizeLib, self, [scope, id])


__all__ = ["DDBSizeLib", "__jsii_assembly__"]

publication.publish()
