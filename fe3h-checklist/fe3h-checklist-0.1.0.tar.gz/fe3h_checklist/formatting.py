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

from colorama import Fore, Style


def color_character_names(string: str) -> str:
    """
    Colors character names in their respective house colors
    :param string: The string to format
    :return: The formatted string
    """
    for color, house in [
        (Fore.LIGHTRED_EX, [
            "Edelgard",
            "Hubert",
            "Ferdinand",
            "Linhardt",
            "Caspar",
            "Petra",
            "Bernadetta",
            "Dorothea"
        ]),
        (Fore.LIGHTBLUE_EX, [
            "Dimitri",
            "Dedue",
            "Felix",
            "Sylvain",
            "Ashe",
            "Annette",
            "Mercedes",
            "Ingrid"
        ]),
        (Fore.LIGHTYELLOW_EX, [
            "Claude",
            "Hilda",
            "Lorenz",
            "Raphael",
            "Ignatz",
            "Lysithea",
            "Marianne",
            "Leonie"
        ]),
        (Fore.LIGHTGREEN_EX, [
            "Rhea",
            "Sothis",
            "Seteth",
            "Flayn",
            "Hanneman",
            "Manuela",
            "Alois",
            "Gilbert",
            "Catherine",
            "Shamir",
            "Cyril"
        ]),
        (Fore.LIGHTWHITE_EX, [
            "Byleth M",
            "Byleth F"
        ]),
    ]:
        for character in house:
            string = string.replace(character, "{}{}{}".format(
                color, character, Style.RESET_ALL
            ))
    return string
