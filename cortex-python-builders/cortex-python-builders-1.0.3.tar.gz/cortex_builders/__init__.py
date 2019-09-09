"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pkg_resources
from .builder_factory import BuilderFactory as Builder
from .builder_factory import LocalBuilderFactory as LocalBuilder
from .dataset_builder import DatasetBuilder
from .action_builder import ActionBuilder
from .connection_builder import ConnectionBuilder
from .schema_builder import SchemaBuilder
from .skill_builder import SkillBuilder
from .exceptions import BuilderException

__version__ = pkg_resources.get_distribution("cortex-python-builders").version

__all__ = [
    '__version__',
    'load_ipython_extension',
    'Builder',
    'LocalBuilder',
    'DatasetBuilder',
    'ActionBuilder',
    'SkillBuilder',
    'SchemaBuilder',
    'ConnectionBuilder',
    'BuilderException'
]


def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    from .magics import CortexMagics
    ipython.register_magics(CortexMagics)
