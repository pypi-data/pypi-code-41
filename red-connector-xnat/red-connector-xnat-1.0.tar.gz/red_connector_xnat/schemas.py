SEND_FILE_SCHEMA = {
    'type': 'object',
    'properties': {
        'baseUrl': {'type': 'string'},
        'project': {'type': 'string'},
        'subject': {'type': 'string'},
        'session': {'type': 'string'},
        'containerType': {'enum': ['scans', 'reconstructions', 'assessors']},
        'container': {'type': 'string'},
        'resource': {'type': 'string'},
        'xsiType': {'type': 'string'},
        'file': {'type': 'string'},
        'overwriteExistingFile': {'type': 'boolean'},
        'auth': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'}
            },
            'additionalProperties': False,
            'required': ['username', 'password']
        },
        'disableSSLVerification': {'type': 'boolean'},
    },
    'additionalProperties': False,
    'required': ['baseUrl', 'project', 'subject', 'session', 'containerType', 'container', 'file', 'auth']
}

RECEIVE_FILE_SCHEMA = {
    'oneOf': [{
        'type': 'object',
        'properties': {
            'baseUrl': {'type': 'string'},
            'project': {'type': 'string'},
            'subject': {'type': 'string'},
            'session': {'type': 'string'},
            'containerType': {'enum': ['scans', 'reconstructions', 'assessors']},
            'container': {'type': 'string'},
            'resource': {'type': 'string'},
            'file': {'type': 'string'},
            'auth': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'additionalProperties': False,
                'required': ['username', 'password']
            },
            'disableSSLVerification': {'type': 'boolean'},
        },
        'additionalProperties': False,
        'required': [
            'baseUrl', 'project', 'subject', 'session', 'containerType', 'container', 'resource', 'file', 'auth'
        ]
    }, {
        'type': 'object',
        'properties': {
            'baseUrl': {'type': 'string'},
            'project': {'type': 'string'},
            'subject': {'type': 'string'},
            'session': {'type': 'string'},
            'resource': {'type': 'string'},
            'file': {'type': 'string'},
            'auth': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'additionalProperties': False,
                'required': ['username', 'password']
            },
            'disableSSLVerification': {'type': 'boolean'},
        },
        'additionalProperties': False,
        'required': ['baseUrl', 'project', 'subject', 'session', 'resource', 'file', 'auth']
    }, {
        'type': 'object',
        'properties': {
            'baseUrl': {'type': 'string'},
            'project': {'type': 'string'},
            'subject': {'type': 'string'},
            'resource': {'type': 'string'},
            'file': {'type': 'string'},
            'auth': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'additionalProperties': False,
                'required': ['username', 'password']
            },
            'disableSSLVerification': {'type': 'boolean'},
        },
        'additionalProperties': False,
        'required': ['baseUrl', 'project', 'subject', 'resource', 'file', 'auth']
    }, {
        'type': 'object',
        'properties': {
            'baseUrl': {'type': 'string'},
            'project': {'type': 'string'},
            'resource': {'type': 'string'},
            'file': {'type': 'string'},
            'auth': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'additionalProperties': False,
                'required': ['username', 'password']
            },
            'disableSSLVerification': {'type': 'boolean'},
        },
        'additionalProperties': False,
        'required': ['baseUrl', 'project', 'resource', 'file', 'auth']
    }]
}
