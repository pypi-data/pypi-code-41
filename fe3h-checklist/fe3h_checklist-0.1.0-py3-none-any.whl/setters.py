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

import sys
from fe3h_checklist.support_encoding import encode_support_levels
from fe3h_checklist.ods_interface import load_support_levels_info, \
    load_support_levels, save_support_levels


def set_support_level(char_one: str, char_two: str, level: str):
    """
    Sets the support level for two characters and saves it.
    :param char_one: The first character
    :param char_two: The second character
    :param level: The support level
    :return: None
    """
    level = encode_support_levels(level)
    current = load_support_levels()
    info = load_support_levels_info()

    if char_two not in info[char_one]:
        print("Invalid character combination")
        sys.exit(1)
    elif level not in info[char_one][char_two]:
        print("Invalid support level")
        sys.exit(1)
    else:
        current[char_one][char_two] = level
        current[char_two][char_one] = level
        save_support_levels(current)
