# Copyright 2018 Intel, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sushy.resources import base

from rsd_lib import base as rsd_lib_base
from rsd_lib import utils as rsd_lib_utils


class IntelRackScaleField(base.CompositeField):

    calculation_precision = base.Field("CalculationPrecision")
    """This property specifies the precision of a calculated metric
       (calculated metric shall be aligned to a value specified by This
       property .
    """

    discrete_metric_type = base.Field("DiscreteMetricType")
    """This array property specifies possible values of a discrete metric."""


class OemField(base.CompositeField):

    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """Intel Rack Scale Design specific properties."""


class CalculationParamsTypeCollectionField(base.ListField):

    source_metric = base.Field("SourceMetric")
    """The metric property used as the input into the calculation."""

    result_metric = base.Field("ResultMetric")
    """The metric property used to store the results of the calculation."""


class WildcardCollectionField(base.ListField):

    name = base.Field("Name")
    """The name of Wildcard."""

    values = base.Field("Values")
    """An array of values to substitute for the wildcard."""


class MetricDefinition(rsd_lib_base.ResourceBase):
    """MetricDefinition resource class

       A definition of a metric.
    """

    implementation = base.Field("Implementation")
    """Specifies how the sensor is implemented."""

    calculable = base.Field("Calculable")
    """Caculatability of this Metric."""

    units = base.Field("Units")
    """Units of measure for this metric."""

    data_type = base.Field("DataType")
    """The data type of the corresponding metric values."""

    is_linear = base.Field("IsLinear", adapter=bool)
    """Indicates linear or non-linear values."""

    metric_type = base.Field("MetricType")
    """Specifies the type of metric provided."""

    wildcards = WildcardCollectionField("Wildcards")
    """Wildcards used to replace values in AppliesTo and Calculates metric
       property arrays.
    """

    metric_properties = base.Field("MetricProperties")
    """A collection of URI for the properties on which this metric definition
       is defined.
    """

    calculation_parameters = CalculationParamsTypeCollectionField(
        "CalculationParameters"
    )
    """Specifies the resource properties (metric) which are characterized by
       this definition.
    """

    physical_context = base.Field("PhysicalContext")
    """Specifies the physical context of the sensor."""

    sensor_type = base.Field("SensorType")
    """This property represents the type of sensor that this resource
       represents.
    """

    sensing_interval = base.Field("SensingInterval")
    """This property specifies the time interval between when a metric or
       sensor reading is updated.
    """

    discrete_values = base.Field("DiscreteValues")
    """This array property specifies possible values of a discrete metric."""

    precision = base.Field("Precision", adapter=rsd_lib_utils.num_or_none)
    """Number of significant digits in the Reading described by
       MetricProperties field.
    """

    accuracy = base.Field("Accuracy", adapter=rsd_lib_utils.num_or_none)
    """Estimated percent error of measured vs. actual values."""

    calibration = base.Field("Calibration", adapter=rsd_lib_utils.num_or_none)
    """Specifies the calibration offset added to the Reading to obtain an
       accurate value.
    """

    time_stamp_accuracy = base.Field("TimeStampAccuracy")
    """Accuracy of the timestamp."""

    min_reading_range = base.Field(
        "MinReadingRange", adapter=rsd_lib_utils.num_or_none
    )
    """Minimum value for Reading."""

    max_reading_range = base.Field(
        "MaxReadingRange", adapter=rsd_lib_utils.num_or_none
    )
    """Maximum value for Reading."""

    calculation_algorithm = base.Field("CalculationAlgorithm")
    """This property specifies the calculation which is performed on a source
       metric to obtain the metric being defined.
    """

    calculation_time_interval = base.Field("CalculationTimeInterval")
    """This property specifies the time interval over which a calculated
       metric algorithm is performed.
    """

    oem = OemField("Oem")
    """Oem specific properties."""


class MetricDefinitionCollection(rsd_lib_base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return MetricDefinition
