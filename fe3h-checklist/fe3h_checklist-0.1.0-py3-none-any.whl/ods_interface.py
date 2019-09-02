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

from typing import Dict
from pyexcel_ods import read_data, save_data
from fe3h_checklist import support_levels_file, support_levels_info_file
from fe3h_checklist.support_encoding import encode_support_levels, \
    decode_support_levels


def load_support_levels() -> Dict[str, Dict[str, str]]:
    """
    Loads the information about support levels from the ODS file
    and puts the data into a dictionary mapping the character's current
    support levels to each other
    :return: The dictionary mapping the support levels to characters.
             Example: {"Byleth M": {"Edelgard": "A"}}
    """
    return load_table(support_levels_file, "SupportLevels")


def load_support_levels_info() -> Dict[str, Dict[str, str]]:
    """
    Loads the information about support level info from the ODS file
    and puts the data into a dictionary mapping the character's support
    levels to each other
    :return: The dictionary mapping the support levels to characters.
             Example: {"Byleth M": {"Edelgard": "CBAS"}}
    """
    return load_table(support_levels_info_file, "SupportLevelsInfo")


def load_table(ods_file: str, sheet_name: str) -> Dict[str, Dict[str, str]]:
    """
    Loads a table from an ODS file.
    Assumptions about the ODS file:
        - Character names at the top and left side of the table
    :param ods_file: The ODS file from which to load the data
    :param sheet_name: The sheet name from which to load the data
    :return: A dictionary mapping the characters to each other and
             containing the value mapped to both of them.
             Example: {"Byleth M": {"Edelgard": "CBAS"}}
    """
    data_map = {}
    data_sheet = dict(read_data(ods_file))[sheet_name]

    names = data_sheet.pop(0)
    names.pop(0)

    for row in data_sheet:
        name = row.pop(0)
        data_map[name] = {}

        for i, entry in enumerate(row):
            if entry != "":
                data_map[name][names[i]] = encode_support_levels(entry)

    return data_map


def save_support_levels(support_levels: Dict[str, Dict[str, str]]):
    """
    Saves the support levels to file
    :param support_levels: The support levels to save
    :return: None
    """
    write_table(support_levels_file, "SupportLevels", support_levels)


def write_table(
        ods_file: str,
        sheet_name: str,
        data: Dict[str, Dict[str, str]]
):
    """
    Writes the content of a dictionary mapping characters to each other
    to an ODS file.
    :param ods_file: The ODS file to write to
    :param sheet_name: The sheet name to write to
    :param data: The data to write
    :return: None
    """
    new_sheet = [[""]]
    for char_one in data:
        new_sheet[0].append(char_one)
        new_row = [char_one]
        for char_two in data:
            entry = data[char_one].get(char_two, "")
            entry = decode_support_levels(entry, for_sheet=True)
            new_row.append(entry)
        new_sheet.append(new_row)

    ods = dict(read_data(ods_file))
    ods[sheet_name] = new_sheet
    save_data(ods_file, ods)
