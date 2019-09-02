import hydrus

# Encoding used by Hydrus to create metadata files
HYDRUS_ENCODING = 'UTF-8'


def cli_request_api_key(name, permissions, verify=True, api_url=hydrus.DEFAULT_API_URL):
    while True:
        input(('Navigate to "services->review services->local->client api" in the Hydrus client and click "add->from '
               'api request". Then press enter to continue...'))
        access_key = hydrus.Client(url=api_url).request_new_permissions(name, permissions)
        input('Press OK and then apply in the Hydrus client dialog. Then press enter to continue...')

        client = hydrus.Client(access_key, api_url)
        if verify and not verify_permissions(client, permissions):
            granted_permissions = client.verify_access_key()['basic_permissions']
            print(('The granted permissions ({}) differ from the requested permissions ({}), please grant all requested'
                   ' permissions.').format(granted_permissions, permissions))
            continue

        return access_key


# Useful in combination with search_files() and file_metadata(), since file_metadata() seems to raise a ServerError
# after exceeding a certain number of requested items (in my tests ~1344).
def yield_chunks(sequence, chunk_size, offset=0):
    while offset < len(sequence):
        yield sequence[offset:offset + chunk_size]
        offset += chunk_size


def read_hydrus_metadata_file(path):
    tags = set()
    with open(path, encoding=HYDRUS_ENCODING) as file:
        for line in file:
            if line.strip():
                tags.add(line)

    return tags


def verify_permissions(client, permissions, exact=False):
    granted_permissions = set(client.verify_access_key()['basic_permissions'])
    return granted_permissions == set(permissions) if exact else granted_permissions.issuperset(permissions)
