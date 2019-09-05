# -*- coding: utf-8 -*-
"""
This module implements writing CSV format events.
"""

import six
from unicodecsv import DictWriter

def csv_header(obj, print_header=False):
    """
    Returns a set of existent field names returned by Magnet v2 API alerts.
    """
    alert_header_fieldnames = ['organization_id', 'id', 'aggFirst', 'aggLast', 'aggCount', 
    'confidence', 'batchDate', 'batchTime', 'logDate', 'updatedAt', 'createdAt', 'status', 
    'netBlocked', 'netDeviceTypes', 'netApp', 
    'netSrcId', 'netSrcUser', 
    'netSrcIp', 'netSrcIpRdomain', 'netSrcProcessId',
    'netDstIp', 'netDstPort', 'netDstDomain', 'netDstIpRdomain',
    'netSrcProcessMd5', 'netL4proto','netL7proto', 'netL7protoSuccessful', 
    'authority', 'soaEmail', 'soaHost', 'country', 'cdnName', 'asName', 'asNumber',
    'matches', 'tags', 
    'explain_country_ratio', 'explain_country_label', 
    'explain_asNumber_ratio', 'explain_asNumber_label', 
    'explain_netDstIpRdomainOrgSuffix_ratio', 'explain_netDstIpRdomainOrgSuffix_label', 
    'explain_netDstIpRdomainPublicSuffix_ratio', 'explain_netDstIpRdomainPublicSuffix_label', 
    'explain_bgpPrefix_ratio', 'explain_bgpPrefix_label',
    'explain_netDstDomainSoaAuthority_ratio', 'explain_netDstDomainSoaAuthority_label',
    'explain_netDstDomainOrgSuffix_ratio', 'explain_netDstDomainOrgSuffix_label',
    'explain_netDstDomainPublicSuffix_ratio', 'explain_netDstDomainPublicSuffix_label'
    ]

    if print_header:
        csv_writer = DictWriter(obj, fieldnames=alert_header_fieldnames)
        csv_writer.writeheader()
    else:
        return(alert_header_fieldnames)


def convert_alert_csv(obj, alert, organization):
    """
    Converts a Niddel Magnet v2 API alert into CSV format.
    :param obj: file-like object in binary mode to write to
    :param alert: dict containing a Niddel Magnet v2 API
    :param alert: UUID object for the organization ID
    :return: an str / bytes object containing a CSV event
    """

    alert_header = csv_header(obj, print_header=False)

    # normalize JSON based on default header
    normalized_alert = dict.fromkeys(alert_header)

    for fieldname in alert_header:
        if fieldname in ['netDeviceTypes', 'tags']:
            _alert_field = alert.get(fieldname, None)
            if _alert_field:
                normalized_alert[fieldname] = unicode(';'.join(map(str, _alert_field)))
        else:
            normalized_alert[fieldname] = unicode(alert.get(fieldname, 'NA'))

    # Unnest EXPLAIN json
    alert_explain = alert.get('explain')
    for key in alert_explain.keys():
        _explain = alert_explain.get(key, None)
        normalized_alert[str('explain_'+ key +'_ratio')] = unicode(_explain.get('ratio', 'NA'))
        normalized_alert[str('explain_'+ key +'_label')] = unicode(_explain.get('label', 'NA'))

    normalized_alert['organization_id'] = unicode(organization)

    csv_writer = DictWriter(obj, fieldnames=alert_header, restval='NA')

    # write alert content based on default header
    csv_writer.writerow(normalized_alert)
