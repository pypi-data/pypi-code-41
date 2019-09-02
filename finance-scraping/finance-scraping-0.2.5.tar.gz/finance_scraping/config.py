from configparser import ConfigParser


def get_config():
    """
    Read configuration file, perform appropriate typ conversion
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
        map(int, requests_config['retry_on'].split(','))
    )

    requests_params['timeout'] = int(requests_config['timeout'])

    return {
        'AWS': config['AWS'],
        'REQUESTS': requests_params,
        'SCRAPING': config['SCRAPING'],
        'DATABASE': config['DATABASE']
    }


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
