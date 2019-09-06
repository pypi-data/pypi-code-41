# _*_ coding: utf-8 _*_
from fhirpath.dialects.elasticsearch import ElasticSearchDialect as BaseDialect
from fhirpath.dialects.elasticsearch import ES_PY_OPERATOR_MAP
from fhirpath.interfaces import IFhirPrimitiveType

import operator


__author__ = "Md Nazrul Islam<email2nazrul@gmail.com>"


class ElasticSearchDialect(BaseDialect):
    """ """

    def apply_security(self, securities, body_structure):
        """ """
        if "allowedRolesAndUsers" in securities:
            values = securities["allowedRolesAndUsers"]
            if isinstance(values, (str, bytes)):
                values = [values]
            terms = {"terms": {"allowedRolesAndUsers": values}}
            body_structure["query"]["bool"]["filter"].append(terms)

        if "effectiveRange" in securities:
            value = IFhirPrimitiveType(securities["effectiveRange"])
            # just validation
            value.to_python()
            range_ = [
                {
                    "range": {
                        "effectiveRange.effectiveRange1": {
                            ES_PY_OPERATOR_MAP[operator.le]: value
                        }
                    }
                },
                {
                    "range": {
                        "effectiveRange.effectiveRange2": {
                            ES_PY_OPERATOR_MAP[operator.ge]: value
                        }
                    }
                },
            ]

            body_structure["query"]["bool"]["filter"].extend(range_)

    def _clean_up(self, body_structure):
        """ """
        # add default sort
        if "_score" not in str(body_structure["sort"]):
            body_structure["sort"].append("_score")
        super(ElasticSearchDialect, self)._clean_up(body_structure)
