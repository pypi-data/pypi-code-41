# -*- coding: utf-8 -*-
# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Task for executing hindsight."""

from __future__ import unicode_literals

import os

from turbinia.evidence import TextFile
from turbinia.workers import TurbiniaTask


class HindsightTask(TurbiniaTask):
  """Task to execute hindsight."""

  def __init__(self):
    super(HindsightTask, self).__init__()

  def run(self, evidence, result):
    """Task to execute hindsight."""

    # Create the new Evidence object that will be generated by this Task.
    output_evidence = TextFile()

    # Create a path that we can write the new file to.
    output_file_path = os.path.join(self.output_dir, 'hindsight_report')
    output_evidence.local_path = output_file_path

    # Create a path for the log file
    hindsight_log = os.path.join(self.output_dir, 'hindsight.log')

    cmd = [
        'hindsight.py', '-i', evidence.local_path, '--format',
        evidence.output_format, '--browser_type', evidence.browser_type,
        '--output', output_file_path, '-l', hindsight_log
    ]

    result.log('Running hindsight as [{0:s}]'.format(' '.join(cmd)))
    self.execute(
        cmd, result, log_files=[hindsight_log], new_evidence=[output_evidence],
        close=True)

    return result
