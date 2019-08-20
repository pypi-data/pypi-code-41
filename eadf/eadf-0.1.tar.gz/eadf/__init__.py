# Copyright 2019 S. Pawar, S. Semper
#     https://www.tu-ilmenau.de/it-ems/
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

r"""
Geometry-based MIMO channel modelling and a high-resolution parameter
estimation are applications in which a precise description of the radiation
pattern of the antenna arrays is required. In this package we implement an
efficient representation of the polarimetric antenna response, which we refer
to as the Effective Anerture Distribution Function (EADF). High-resolution
parameter estimation are applications in which this reduced description permits
us to efficiently interpolate the beam pattern to gather the antenna response
for an arbitrary direction in azimuth and elevation. Moreover, the EADF
provides a continuous description of the array manifold and its derivatives
with respect to azimuth and elevation. The latter is valuable for the
performance evaluation of an antenna array as well as for gradient-based
parameter estimation techniques.
"""

from .eadf import EADF
