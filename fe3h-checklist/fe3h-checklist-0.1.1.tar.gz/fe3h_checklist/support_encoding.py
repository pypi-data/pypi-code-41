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


def encode_support_levels(support_levels: str) -> str:
    """
    Converts a support level string into something that can easily be indexed.
    The existance of a '+' rank like 'C+' is stored in the info sheet as
    "CC" and therefore uses up two spaces, making indexing hard.
    So we convert these '+' support levels like this:
        C+ -> 1
        B+ -> 2
        A+ -> 3
    :param support_levels: The support level string to encode
    :return: The encoded support level string
    """
    return support_levels\
        .replace("C+", "1")\
        .replace("B+", "2")\
        .replace("A+", "3")\
        .replace("CC", "C1")\
        .replace("BB", "B2")\
        .replace("AA", "A3")


def decode_support_levels(encoded: str, for_sheet: bool = False):
    """
    Decodes the support levels back into a human-readable format
    :param encoded: The encoded support level
    :param for_sheet: Changes the support levels into the format used in the
                      data sheet (e.g. C1 -> CC)
    :return: The decoded support level
    """
    if for_sheet:
        return encoded \
            .replace("1", "C") \
            .replace("2", "B") \
            .replace("3", "A")
    else:
        return encoded\
            .replace("1", "C+")\
            .replace("2", "B+")\
            .replace("3", "A+")
