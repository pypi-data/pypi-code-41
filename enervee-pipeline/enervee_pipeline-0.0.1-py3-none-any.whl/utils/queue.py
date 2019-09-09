from enervee_pipeline import config
import boto3
import json


def get_sqs_conn():
    """
    Returns an sqs client
    :return botocore.client.SQS sqs_client: SQS client
    """
    return boto3.client(
        'sqs',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_REGION,
    )


def get_sqs_resource():
    """
    Returns an sqs resource
    :return botocore.resource.SQS sqs_resource: SQS resource
    """
    return boto3.resource(
        'sqs',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_REGION,
    )


def get_sqs_queue(sqs_client, queue_name):
    """
    Given a queue name, returns the boto3 Queue object corresponding to the
    queue in the current environment.
    :param botocore.client.SQS sqs_client: SQS client
    :param str queue_name: The queue name
    :return boto3.resources.factory.sqs.Queue
    """
    sqs_resource = get_sqs_resource()
    try:
        sqs_queue = sqs_resource.get_queue_by_name(QueueName=queue_name)
    except sqs_client.exceptions.QueueDoesNotExist:
        sqs_queue = sqs_resource.create_queue(QueueName=queue_name)

    sqs_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
    return sqs_queue, sqs_url


def enqueue_message(sqs_client, queue_url, message_body, message_attributes={}):
    """
    Given a queue name, returns the boto3 Queue object corresponding to the
    queue in the current environment.
    :param botocore.client.SQS sqs_client: SQS client
    :param str queue_url: The queue url
    :param dict message_body: JSON serializable message metadata we want to send
    :param dict message_attributes: (optional) Metadata to configure SQS message attr
    """
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body),
        MessageAttributes=message_attributes
    )
