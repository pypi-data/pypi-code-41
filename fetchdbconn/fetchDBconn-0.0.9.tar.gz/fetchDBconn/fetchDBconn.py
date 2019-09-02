
import boto3
import ast

def db_details(secret_name,region_name,aws_key,aws_secret):
    secret_name = secret_name 
    region_name = region_name
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        aws_access_key_id = aws_key, 
        aws_secret_access_key = aws_secret #
    )
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    return ast.literal_eval(get_secret_value_response['SecretString'])

def hello():
    print("hello")