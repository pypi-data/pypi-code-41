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

from typing import Dict, Tuple


def calculate_remaining_support_levels(
        character: str,
        support_levels: Dict[str, Dict[str, str]],
        support_levels_info: Dict[str, Dict[str, str]]
) -> Tuple[int, Dict[str, int]]:
    """
    Calculates how many support levels are left for a character.
    This calculates both the total amount of support levels left for the
    character as well as the remaining support levels with individual
    characters.
    :param character: The character for which to calculate the remaining
                      support levels
    :param support_levels: The current support levels
    :param support_levels_info: The support levels info
    :return: A tuple consisting of the total remaining support levels and
             a dictionary mapping individual support levels to characters
    """
    total = 0
    remaining = {}

    for support, info in support_levels_info[character].items():
        current = support_levels[character][support]
        try:
            position = info.index(current)
            diff = len(info) - position - 1

            # TODO REMOVE ONCE DEVELOPMENT COMPLETE
            index = -1 if diff == 0 else -(diff + 1)
            calculated_rank = info[index]
            if current != calculated_rank:
                print("RANK ERROR!")

        except ValueError:
            diff = len(info)

        total += diff
        remaining[support] = diff

    return total, remaining


def calculate_max_support_rank(
        char_one: str,
        char_two: str,
        support_levels_info: Dict[str, Dict[str, str]]
) -> str:
    """
    Calculates the maximal support level between two characters
    :param char_one: The first character
    :param char_two: The second character
    :param support_levels_info: The support levels info
    :return: The maximal rank
    """
    return support_levels_info[char_one][char_two][-1]
