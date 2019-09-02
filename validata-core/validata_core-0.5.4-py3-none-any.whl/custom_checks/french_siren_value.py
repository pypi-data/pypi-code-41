# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import stdnum.fr.siren
from goodtables.registry import check
from goodtables.error import Error


@check("french-siren-value", type="custom", context="body")
class FrenchSirenValue(object):
    def __init__(self, column, **options):
        self.__column = column

    def check_row(self, cells):
        # Get cell
        cell = None
        for item in cells:
            if "header" not in item:
                # Skip columns without headers. This can occur in particular with formatted Excel files.
                continue
            if self.__column in [item["column-number"], item["header"]]:
                cell = item
                break

        # Check cell
        if not cell:
            return

        # Check value
        value = cell.get("value")
        if not stdnum.fr.siren.is_valid(value):
            message = 'La valeur "{value}" n\'est pas un numéro SIREN français valide.'
            message_substitutions = {"value": value}
            error = Error(
                "french-siren-value",
                cell,
                message=message,
                message_substitutions=message_substitutions,
            )
            return [error]
