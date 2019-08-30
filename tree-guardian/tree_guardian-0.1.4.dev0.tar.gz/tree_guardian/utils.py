import os


GITIGNORE_FILENAME = '.gitignore'


def get_gitignored():
    if not os.path.isfile(GITIGNORE_FILENAME):
        return set()

    with open(GITIGNORE_FILENAME) as gitignore:
        return set(line.strip() for line in gitignore.readlines()
                   if line.strip() and not line.strip().startswith('#'))
