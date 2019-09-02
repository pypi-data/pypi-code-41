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

from fe3h_checklist.ods_interface import load_support_levels, \
    load_support_levels_info
from fe3h_checklist.calc import calculate_remaining_support_levels, \
    calculate_max_support_rank
from fe3h_checklist.support_encoding import decode_support_levels
from fe3h_checklist.formatting import color_character_names


def print_remaining_support_levels(no_byleth: bool, multi_line: bool):
    """
    Prints the remaining support levels for all characters and orders
    them in a descending order.
    :param no_byleth: Whether or not to include support levels with Byleth
    :param multi_line: Whether or not to use multiple lines per character
    :return: None
    """
    support_levels = load_support_levels()
    support_levels_info = load_support_levels_info()

    ranking = []
    for character in support_levels_info:

        if "Byleth" in character and no_byleth:
            continue

        total, remaining = calculate_remaining_support_levels(
            character, support_levels, support_levels_info
        )

        if "Byleth" not in character and no_byleth:
            total -= remaining.pop("Byleth M", 0)
            total -= remaining.pop("Byleth F", 0)

        ranking.append((character, total, remaining))

    ranking.sort(key=lambda x: x[1], reverse=True)
    max_char_length = len(max(ranking, key=lambda x: len(x[0]))[0])

    for rank, (character, total, remaining) in enumerate(ranking):

        supports = []
        for support, diff in remaining.items():

            if diff == 0:
                continue

            current_rank = support_levels[character][support]
            max_rank = calculate_max_support_rank(
                character, support, support_levels_info
            )

            supports.append("{}({}/{})".format(
                support.ljust(max_char_length) + (" " if multi_line else ""),
                decode_support_levels(current_rank),
                decode_support_levels(max_rank)
            ).ljust(max_char_length + 7))

        if multi_line:
            supports = ("\n" + " " * (max_char_length + 13)).join(supports)
        else:
            supports = "[" + ", ".join(supports) + "]"

        print(color_character_names("{}({}): {} -> {}".format(
            str(rank + 1).rjust(2),
            str(total).rjust(3),
            character.ljust(max_char_length),
            supports
        )))
