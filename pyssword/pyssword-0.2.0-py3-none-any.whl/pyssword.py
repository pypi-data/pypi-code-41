import string
import secrets
import click

from . import util


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
ALPHABET = dict(
    nopunctuation=string.ascii_letters + string.digits,
    digits=string.digits,
    small=string.ascii_letters + string.digits + '!?@#$%&*+-_.,',
    full=string.ascii_letters + string.digits + string.punctuation,
)


@click.command(options_metavar='<options>', context_settings=CONTEXT_SETTINGS)
@click.argument('size', default=16, type=click.IntRange(10, None), metavar='<size>')
@click.option('-s', '--small', is_flag=True, help='Small set of valid punctuation symbols for password.')
@click.option('-d', '--digits', is_flag=True, help='Only digits for password.')
@click.option('-n', '--nopunctuation', is_flag=True, help="Don't add punctuation symbols for password.")
@util.doc(
    f"""Make random passwords for given <size> and optionally chosen alphabet type.

    \b
    size:               Password length (min: 10).
    alphabet type:
        default         {ALPHABET['full']}
        small           {ALPHABET['small']}
        nopunctuation   {ALPHABET['nopunctuation']}
        digits          {ALPHABET['digits']}
    """
)
def run(size, **kwargs):
    if kwargs['digits']:
        password = ''.join(secrets.choice(ALPHABET['digits']) for i in range(size))
        print(password)
    else:
        if kwargs['nopunctuation']:
            alphabet = ALPHABET['nopunctuation']
        elif kwargs['small']:
            alphabet = ALPHABET['small']
        else:
            alphabet = ALPHABET['full']

        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(size))

            if (not starts_with_punctuation(password) and
                    (has_punctuation(password) or kwargs['nopunctuation']) and
                    has_lowercase(password, 3) and
                    has_uppercase(password, 3) and
                    has_digits(password, 3)
                ):
                print(password)
                break


def starts_with_punctuation(password):
    return password[0] in string.punctuation


def has_punctuation(password):
    return any(c in string.punctuation for c in password)


def has_uppercase(password, times):
    return sum(c.isupper() for c in password) >= times


def has_lowercase(password, times):
    return sum(c.islower() for c in password) >= times


def has_digits(password, times):
    return sum(c.isdigit() for c in password) >= times


if __name__ == '__main__':
    run()
