# from awsparameter.aws_s3_kms_parameter import Parameters
import boto3
import json
import base64
import logging
logger = logging.getLogger()


def encrypt_text_with_kms(config_dict, key_id, kms_client=None):
    if kms_client is None:
        kms_client = boto3.client('kms',
                                  aws_access_key_id=None,
                                  aws_secret_access_key=None
                                  )
    config_text = json.dumps(config_dict)
    key = 'alias/%s' % key_id
    try:
        response = kms_client.encrypt(
            KeyId=key,
            Plaintext=config_text
        )
        encrypted_ciphertext = base64.b64encode(response["CiphertextBlob"])
    except Exception as err:
        logger.error(err)
        raise

    return encrypted_ciphertext


def upload_s3(key_bucket, ssm_key_alias, key_name, encoded_ciphertext, s3_client=None):
    if s3_client is None:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=None,
                                 aws_secret_access_key=None
                                 )
    key = 'alias/%s' % ssm_key_alias
    if '.json' not in key_name:
        key_name = key_name + '.json'
    try:
        response = s3_client.put_object(
            ACL='private',
            Body=encoded_ciphertext,
            Bucket=key_bucket,
            ContentType="application/json",
            ServerSideEncryption="aws:kms",
            SSEKMSKeyId=key,
            Key=key_name
        )
    except Exception as err:
        logger.error(err)
        raise
    return response


def get_aws_config_from_bucket(s3_client, ssm_key, key_bucket):
    if '.json' not in ssm_key:
        s3_key = ssm_key + '.json'
    else:
        s3_key = ssm_key

    response = s3_client.get_object(
        Bucket=key_bucket,
        Key=s3_key
    )
    decoded_res = response['Body'].read()
    return decoded_res


def decrypt_text_with_kms(key_bucket, saved_bucket_key, kms_client=None, s3_client=None):
    if kms_client is None:
        kms_client = boto3.client('kms',
                                  aws_access_key_id=None,
                                  aws_secret_access_key=None
                                  )
    if s3_client is None:
        s3_client = boto3.client('s3',
                                 aws_access_key_id=None,
                                 aws_secret_access_key=None
                                 )

    endcoded_text = get_aws_config_from_bucket(s3_client, saved_bucket_key, key_bucket)
    cipher_text_blob = base64.b64decode(endcoded_text)
    decrypt_text = kms_client.decrypt(
        CiphertextBlob=bytes(cipher_text_blob)
    )
    encoded_txt = json.loads(decrypt_text['Plaintext'])
    return encoded_txt

