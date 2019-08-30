# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TFX ExampleValidator component definition."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from typing import Optional, Text

from tfx.components.base import base_component
# from tfx.types.component_spec import ChannelParameter
from salure_tfx_extensions.components.schema_gen.executor import Executor
from tfx import types
from tfx.types.standard_component_specs import SchemaGenSpec
from tfx.types import channel_utils


# class SchemaGenSpec(types.ComponentSpec):
#     """SchemaGen component spec."""
#
#     PARAMETERS = {}
#     INPUTS = {
#         'stats': ChannelParameter(type_name='ExampleStatisticsPath'),
#     }
#     OUTPUTS = {
#         'output': ChannelParameter(type_name='SchemaPath'),
#     }


class SchemaGen(base_component.BaseComponent):
    """Official TFX SchemaGen component.
    The SchemaGen component uses Tensorflow Data Validation (tfdv) to
    generate a schema from input statistics.
    """

    SPEC_CLASS = SchemaGenSpec
    EXECUTOR_CLASS = Executor

    def __init__(self,
                 stats: types.Channel,
                 output: Optional[types.Channel] = None,
                 name: Optional[Text] = None):
        """Constructs a SchemaGen component.
        Args:
          stats: A Channel of 'ExampleStatisticsPath' type (required if spec is not
            passed). This should contain at least a 'train' split. Other splits are
            currently ignored.
          output: Optional output 'SchemaPath' channel for schema result.
          name: Optional unique name. Necessary iff multiple SchemaGen components
            are declared in the same pipeline.
        """
        output = output or types.Channel(
            type_name='SchemaPath', artifacts=[types.Artifact('SchemaPath')])
        spec = SchemaGenSpec(stats=stats, output=output)
        super(SchemaGen, self).__init__(spec=spec, name=name)
