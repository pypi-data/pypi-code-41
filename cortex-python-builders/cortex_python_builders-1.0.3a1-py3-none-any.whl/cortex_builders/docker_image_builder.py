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

import itertools
from pathlib import Path
import tempfile

import time
import cuid
import tenacity

from cortex.utils import get_logger
from cortex.action import BuilderClient
from .utils.docker_utils import DockerUtils
from .exceptions import BuilderException


log = get_logger(__name__)


class _DockerImageBuilder:

    def build_and_push(self, temp_dir, name, docker_repo, docker_auth):
        raise NotImplementedError

    @staticmethod
    def create_build_context(
        action_type,
        source,
        func_name,
        global_code,
        cortex_sdk_version,
        source_archive,
        base_image,
        using_default_base_image=False,
        requirements=[],
        conda_requirements=[],
    ):
        raise NotImplementedError


class DockerDaemonImageBuilder(_DockerImageBuilder):
    """A Docker image builder that uses the Docker socket."""

    @staticmethod
    def create_build_context(
        action_type,
        source,
        func_name,
        global_code,
        cortex_sdk_version,
        source_archive,
        base_image,
        using_default_base_image=False,
        requirements=[],
        conda_requirements=[],
    ):
        temp_dir = tempfile.mkdtemp()
        return DockerUtils.create_build_context(
            temp_dir,
            action_type,
            source,
            func_name,
            global_code,
            cortex_sdk_version,
            source_archive,
            base_image,
            using_default_base_image,
            requirements,
            conda_requirements,
        )

    def build_and_push(self, temp_dir, name, docker_repo, docker_auth):
        DockerUtils.build_and_push(temp_dir, name, docker_repo, docker_auth)