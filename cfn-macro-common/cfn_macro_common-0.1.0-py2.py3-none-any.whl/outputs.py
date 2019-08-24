# -*- coding: utf-8 -*-

"""
Common functions to return outputs
"""

from troposphere import (
    Output, Export, Sub
)

def cfn_resource_type(object_name, strip=True):
    """
    Returns the Resource Type property removing the AWS:: prefix
    """
    res_type = object_name.resource_type.replace(':', '')
    if strip:
        return res_type.replace('AWS', '')
    return res_type


def comments_outputs(comments, export=False):
    """
    Args:
      comments: list: list of key pair values to add outputs not related to an object
      export: bool: set to True if the value should be exported in the region
    Returns:
        outputs: list: list of Output() object for the Troposphere template
    Comments:
        taken from lambda-my-aws/ozone
    """
    outputs = []
    if isinstance(comments, list):
        for comment in comments:
            if isinstance(comment, dict):
                keys = list(comment.keys())
                args = {
                    'title': keys[0],
                    'Value': comment[keys[0]]
                }
                if export:
                    args['Export'] = Export(Sub(f'${{AWS::StackName}}-{keys[0]}'))
                outputs.append(Output(**args))
    return outputs
