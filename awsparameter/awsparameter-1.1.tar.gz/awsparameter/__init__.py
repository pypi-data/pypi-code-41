# from awsparameter.aws_s3_kms_parameter import Parameters
import boto3
import json
import base64
import logging
logger = logging.getLogger()


def encrypt_text_with_kms(self, config_dict, key_id):
    config_text = json.dumps(config_dict)
    key = 'alias/%s' % key_id
    try:
        response = self.kms_client.encrypt(
            # KeyId=kms_id_arn,
            KeyId=key,
            Plaintext=config_text
        )
        encrypted_ciphertext = base64.b64encode(response["CiphertextBlob"])
    except Exception as err:
        logger.error(err)
        raise

    return encrypted_ciphertext


def upload_s3(self, key_bucket, key_id, encoded_ciphertext):
    key = 'alias/%s' % key_id
    try:
        response = self.s3_client.put_object(
            ACL='private',
            Body=encoded_ciphertext,
            Bucket=key_bucket,
            ContentType="application/json",
            ServerSideEncryption="aws:kms",
            SSEKMSKeyId=key_id,
            Key=key
        )
    except Exception as err:
        logger.error(err)
        raise
    return response


def get_aws_config_from_bucket(s3_client, ssm_key, key_bucket):
    s3_key = ssm_key + '.json'
    response = s3_client.get_object(
        Bucket=key_bucket,
        Key=s3_key
    )
    decoded_res = response['Body'].read()
    return decoded_res


def decrypt_text_with_kms(key_bucket, ssm_key, kms_client=None, s3_client=None):
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

    endcoded_text = get_aws_config_from_bucket(s3_client, ssm_key, key_bucket)
    cipher_text_blob = base64.b64decode(endcoded_text)
    decrypt_text = kms_client.decrypt(
        CiphertextBlob=bytes(cipher_text_blob)
    )
    encoded_txt = json.loads(decrypt_text['Plaintext'])
    return encoded_txt

