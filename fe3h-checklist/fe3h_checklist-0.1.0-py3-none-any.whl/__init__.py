"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of fe3h-checklist.

fe3h-checklist is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

fe3h-checklist is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with fe3h-checklist.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import os

local_dir = os.path.join(os.path.expanduser("~"), ".config/fe3h-checklist")
"""
Directory containing local config files
"""

support_levels_info_file = os.path.join(local_dir, "supportinfo.ods")
"""
File containing the support level info file
"""

support_levels_file = os.path.join(local_dir, "supportlevels.ods")
"""
File containing the support level info file
"""
