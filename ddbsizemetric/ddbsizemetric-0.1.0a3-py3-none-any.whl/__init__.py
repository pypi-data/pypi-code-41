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
__jsii_assembly__ = jsii.JSIIAssembly.load("@richardhboyd/ddbsizemetric", "0.1.0-alpha.3", __name__, "ddbsizemetric@0.1.0-alpha.3.jsii.tgz")
class DDBSizeLib(aws_cdk.core.Construct, metaclass=jsii.JSIIMeta, jsii_type="@richardhboyd/ddbsizemetric.DDBSizeLib"):
    def __init__(self, scope: aws_cdk.core.Construct, id: str, *, polling_frequency: typing.Optional[aws_cdk.core.Duration]=None) -> None:
        """
        :param scope: -
        :param id: -
        :param props: -
        :param polling_frequency: The frequency to poll DynamoDB for table sizes. Must be equal to or greater than 6 hours Default: Duration.hours(6)
        """
        props = DDBSizeLibProps(polling_frequency=polling_frequency)

        jsii.create(DDBSizeLib, self, [scope, id, props])

    @property
    @jsii.member(jsii_name="pollingfrequency")
    def pollingfrequency(self) -> aws_cdk.core.Duration:
        return jsii.get(self, "pollingfrequency")


@jsii.data_type(jsii_type="@richardhboyd/ddbsizemetric.DDBSizeLibProps", jsii_struct_bases=[], name_mapping={'polling_frequency': 'pollingFrequency'})
class DDBSizeLibProps():
    def __init__(self, *, polling_frequency: typing.Optional[aws_cdk.core.Duration]=None):
        """
        :param polling_frequency: The frequency to poll DynamoDB for table sizes. Must be equal to or greater than 6 hours Default: Duration.hours(6)
        """
        self._values = {
        }
        if polling_frequency is not None: self._values["polling_frequency"] = polling_frequency

    @property
    def polling_frequency(self) -> typing.Optional[aws_cdk.core.Duration]:
        """The frequency to poll DynamoDB for table sizes.

        Must be equal to or greater than 6 hours

        default
        :default: Duration.hours(6)
        """
        return self._values.get('polling_frequency')

    def __eq__(self, rhs) -> bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs) -> bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return 'DDBSizeLibProps(%s)' % ', '.join(k + '=' + repr(v) for k, v in self._values.items())


__all__ = ["DDBSizeLib", "DDBSizeLibProps", "__jsii_assembly__"]

publication.publish()
