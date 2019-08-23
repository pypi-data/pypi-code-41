'''
API around 'ss' linux command
'''

import subprocess


def check_port(port):
    '''
    Check for TCP sockets that are on the given port
    '''

    cmd = 'ss sport = :{port} -r'.format(port=port)
    try:
        output = subprocess.check_output(cmd.split())
        output = output.decode('UTF-8').split('\n')
    except (subprocess.CalledProcessError, AttributeError) as e:
        print('Errored occurred with command: "{}"'.format(cmd))

    # Format header
    header = output[0].replace('Address:Port', '').split()

    result = {}
    for index, value in enumerate(''.join(output[1:]).split()):
        result[header[index]] = value

    return result if result else False

