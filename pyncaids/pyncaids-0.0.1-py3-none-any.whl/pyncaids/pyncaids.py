# -*- coding: utf-8 -*-

"""pyncaids.py
   Copyright (c) 2019 Jacek Artymiak
   All Rights Reserved.
"""

class NCA:
    """Represents a register of National Competent Authorities (NCA).
    """

    def __init__(self):
        self.nca_identifiers = [
            {
                "authority_id": "AT-FMA",
                "country": "Austria",
                "authority_name": "Austria Financial Market Authority"
            },
            {
                "authority_id": "BE-NBB",
                "country": "Belgium",
                "authority_name": "National Bank of Belgium"
            },
            {
                "authority_id": "BG-BNB",
                "country": "Bulgaria",
                "authority_name": "Bulgarian National Bank"
            },
            {
                "authority_id": "HR-HNB",
                "country": "Croatia",
                "authority_name": "Croatian National Bank"
            },
            {
                "authority_id": "CY-CBC",
                "country": "Cyprus",
                "authority_name": "Central Bank of Cyprus"
            },
            {
                "authority_id": "CZ-CNB",
                "country": "Czech",
                "authority_name": "Czech National Bank"
            },
            {
                "authority_id": "DK-DFSA",
                "country": "Denmark",
                "authority_name": "Danish Financial Supervisory Authority"
            },
            {
                "authority_id": "EE-FI",
                "country": "Estonia",
                "authority_name": "Estonia Financial Supervisory Authority"
            },
            {
                "authority_id": "FI-FINFSA",
                "country": "Finland",
                "authority_name": "Finnish Financial Supervisory Authority"
            },
            {
                "authority_id": "FR-ACPR",
                "country": "France",
                "authority_name": "Prudential Supervisory and Resolution Authority"
            },
            {
                "authority_id": "DE-BAFIN",
                "country": "Germany",
                "authority_name": "Federal Financial Supervisory Authority"
            },
            {
                "authority_id": "GR-BOG",
                "country": "Greece",
                "authority_name": "Bank of Greece"
            },
            {
                "authority_id": "HU-CBH",
                "country": "Hungary",
                "authority_name": "Central Bank of Hungary"
            },
            {
                "authority_id": "IS-FME",
                "country": "Iceland",
                "authority_name": "Financial Supervisory Authority"
            },
            {
                "authority_id": "IE-CBI",
                "country": "Ireland",
                "authority_name": "Central Bank of Ireland"
            },
            {
                "authority_id": "IT-BI",
                "country": "Italy",
                "authority_name": "Bank of Italy"
            },
            {
                "authority_id": "LI-FMA",
                "country": "Liechtenstein",
                "authority_name": "Financial Market Authority Liechtenstein"
            },
            {
                "authority_id": "LV-FCMC",
                "country": "Latvia",
                "authority_name": "Financial and Capital Markets Commission"
            },
            {
                "authority_id": "LT-BL",
                "country": "Lithuania",
                "authority_name": "Bank of Lithuania"
            },
            {
                "authority_id": "LU-CSSF",
                "country": "Luxembourg",
                "authority_name": "Commission for the Supervision of Financial Sector"
            },
            {
                "authority_id": "NO-FSA",
                "country": "Norway",
                "authority_name": "The Financial Supervisory Authority of Norway"
            },
            {
                "authority_id": "MT-MFSA",
                "country": "Malta",
                "authority_name": "Malta Financial Services Authority"
            },
            {
                "authority_id": "NL-DNB",
                "country": "Netherlands",
                "authority_name": "The Netherlands Bank"
            },
            {
                "authority_id": "PL-PFSA",
                "country": "Poland",
                "authority_name": "Polish Financial Supervision Authority"
            },
            {
                "authority_id": "PT-BP",
                "country": "Portugal",
                "authority_name": "Bank of Portugal"
            },
            {
                "authority_id": "RO-NBR",
                "country": "Romania",
                "authority_name": "National Bank of Romania"
            },
            {
                "authority_id": "SK-NBS",
                "country": "Slovakia",
                "authority_name": "National Bank of Slovakia"
            },
            {
                "authority_id": "SI-BS",
                "country": "Slovenia",
                "authority_name": "Bank of Slovenia"
            },
            {
                "authority_id": "ES-BE",
                "country": "Spain",
                "authority_name": "Bank of Spain"
            },
            {
                "authority_id": "SE-FINA",
                "country": "Sweden",
                "authority_name": "Swedish Financial Supervision Authority"
            },
            {
                "authority_id": "GB-FCA",
                "country": "United Kingdom",
                "authority_name": "Financial Conduct Authority"
            },
        ]

    def nca_by_authority_id(self, authority_id) -> list:
        """Get NCA by authority ID
        """
        authority = [a for a in self.nca_identifiers if a.get("authority_id") == authority_id]
        return authority

    def nca_by_partial_authority_id(self, authority_id_chunk) -> list:
        """Get NCA by partial authority ID
        """
        authority = [a for a in self.nca_identifiers if authority_id_chunk in a.get("authority_id")]
        return authority

    def nca_by_country(self, country) -> list:
        """Get NCA list by country
        """
        authority = [a for a in self.nca_identifiers if a.get("country") == country]
        return authority

    def nca_by_partial_country(self, country_chunk) -> list:
        """Get NCA list by partial country
        """
        authority = [a for a in self.nca_identifiers if country_chunk in a.get("country")]
        return authority

    def nca_by_authority_name(self, authority_name) -> list:
        """Get NCA list by authority name
        """
        authority = [a for a in self.nca_identifiers if a.get("authority_name") == authority_name]
        return authority

    def nca_by_partial_authority_name(self, authority_name_chunk) -> list:
        """Get NCA list by partial authority name
        """
        authority = [a for a in self.nca_identifiers if authority_name_chunk in a.get("authority_name")]
        return authority
