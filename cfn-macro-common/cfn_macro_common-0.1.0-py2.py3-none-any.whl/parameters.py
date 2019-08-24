# -*- coding: utf-8 -*-
"""
Parameters common to all stacks to be used within templates
"""

from troposphere import (
    Parameter
)

CIDR_PATTERN = r'^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$'
ZONE_ID_PATTERN = r'^([A-Z0-9]{14,16})$'

DNS_ZONE_FQDN = Parameter(
    'Route53VpcDnsPrivateZoneFqdnSuffix',
    Type='String',
    Default='cluster.local',
    AllowedPattern=r'[a-z0-9-.]+'
)

VPC_CIDR = Parameter(
    'VpcCidrBlock',
    Type='String',
    AllowedPattern=CIDR_PATTERN
)

VPC_ID = Parameter(
    'VpcId',
    Type='AWS::EC2::VPC::Id'
)

VPC_ZONEID = Parameter(
    'Route53VpDnsPrivateZoneId',
    'VpcZoneId',
    Type='String'
)

VPC_ZONEID_TYPE = Parameter(
    'VpcZoneId',
    Type='AWS::Route53::HostedZone::Id'
)

APPLICATION_SUBNETS = Parameter(
    'ApplicationSubnets',
    Type='List<AWS::EC2::Subnet::Id>'
)

PUBLIC_SUBNETS = Parameter(
    'PublicSubnets',
    Type='List<AWS::EC2::Subnet::Id>'
)

STORAGE_SUBNETS = Parameter(
    'StorageSubnets',
    Type='List<AWS::EC2::Subnet::Id>'
)

KEYPAIR_NAME = Parameter(
    'KeyPairName',
    Type='AWS::EC2::KeyPair::KeyName'
)

SSM_ECS_IMAGE_ID = Parameter(
    'ImageId',
    Type="AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
    Default='/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id'
)
