def random_data(sz=None):
    if sz is None:
        sz = 30 * 80

    def random_line():
        import random
        import string
        return ''.join(random.choice(string.ascii_letters) for x in range(80))

    return '\n'.join(random_line() for x in range(sz/80))

def create_random_temporary_file(sz=None):
    '''
    Create a temporary file with random contents, and return its path.

    The caller is responsible for removing the file when done.

    sz is optional and approximate
    '''
    from baiji.util import tempfile
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write(random_data(sz))
        return f.name
