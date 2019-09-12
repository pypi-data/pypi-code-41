import boto3
import sys
import time

# Requires
# AWS CLI - configured

# Resources
# https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-recordset.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets


def SetDDNS(MyIP,DNSName,HostedZoneId):
    client = boto3.client('route53')
    current_Time = time.strftime("%Y%m%d-%H%M%S")
    response = client.change_resource_record_sets(
        HostedZoneId=f"{HostedZoneId}",
        ChangeBatch={
            'Comment': f"DDNS Update {current_Time}",
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': f"{DNSName}",
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': f"{MyIP}"
                            }
                        ]
                    }
                }
            ]
        }
    )
    return response
    
