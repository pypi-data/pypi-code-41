from configparser import ConfigParser
import os


def get_config():
    """
    Read configuration file, perform appropriate type conversion
    and return the whole configuration.

    :return dict[dict]: configuration
    """
    config = ConfigParser()
    config.read('config.ini')

    # get requests config
    requests_config = config['REQUESTS']
    requests_params = {}
    requests_params['user_agent'] = requests_config['user_agent']
    requests_params['max_retries'] = int(requests_config['max_retries'])
    requests_params['backoff_factor'] = float(
        requests_config['backoff_factor']
    )

    requests_params['retry_on'] = tuple(
        map(int, requests_config['retry_on'].split(',')))

    requests_params['timeout'] = int(requests_config['timeout'])

    return {
        'AWS': config['AWS'],
        'REQUESTS': requests_params,
        'SCRAPING': config['SCRAPING'],
        'DATABASE': config['DATABASE']
    }


def get_environment_variables():
    """
    Read the configuration from the environment variables.

    :return dict[dict]: configuration
    """
    configuration = {}
    configuration['AWS'] = {
        's3_bucket': os.getenv('FINANCE_SCRAPING_S3_BUCKET'),
        'profile': os.getenv('FINANCE_SCRAPING_AWS_PROFILE')
    }
    configuration['REQUESTS'] = {
        'user_agent': os.getenv('FINANCE_SCRAPING_USER_AGENT'),
        'max_retries': int(os.getenv('FINANCE_SCRAPING_MAX_RETRIES')),
        'backoff_factor': float(os.getenv('FINANCE_SCRAPING_BACKOFF_FACTOR')),
        'retry_on': tuple(
            map(int, os.getenv('FINANCE_SCRAPING_RETRY_ON').split(','))),
        'timeout': int(os.getenv('FINANCE_SCRAPING_TIMEOUT'))
    }
    configuration['SCRAPING'] = {
        'urls_s3_key': os.getenv('FINANCE_SCRAPING_URLS_S3_KEY')}
    configuration['DATABASE'] = {
        'database': os.getenv('FINANCE_SCRAPING_DATABASE'),
        'table': os.getenv('FINANCE_SCRAPING_TABLE'),
        'db_user': os.getenv('FINANCE_SCRAPING_DB_USER'),
        'password': os.getenv('FINANCE_SCRAPING_PASSWORD'),
        'host': os.getenv('FINANCE_SCRAPING_HOST'),
        'port': os.getenv('FINANCE_SCRAPING_PORT'),
    }

    return configuration


def configure():
    """
    Get configuration from user's input and write it to 'config.ini'.
    """
    # get existing config
    config = ConfigParser()
    config.read('config.ini')

    print('Please enter configuration values:\n')

    for key in config.keys():

        for k, v in config[key].items():
            # we show the user the default value
            i = input(f'{k} [{v}]: ')

            # wait for user input if no value is set (default or user input)
            while not v and not i:
                i = input(f'{k} [{v}]: ')

            # the eventual user input overwrites the default value
            if i:
                config[key][k] = i

    with open('config.ini', 'w') as config_file:
        config.write(config_file)
