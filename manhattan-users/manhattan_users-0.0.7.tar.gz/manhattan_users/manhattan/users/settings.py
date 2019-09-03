from datetime import timedelta
from werkzeug.contrib.cache import SimpleCache


__all__ = ['UserDefaultConfig']


class DefaultConfig:
    """
    Default settings for the the user access / control set up.
    """

    # Invites

    # The time before an invite to a user to join the application expires
    USER_INVITE_LIFESPAN = timedelta(days=14)


    # Sessions

    # The maximum number of sessions (devices) a user can have registered at
    # any one time.
    USER_MAX_SESSIONS = 12

    # The time before a user's session expires (from the last time the user
    # accessed the application).
    USER_SESSION_LIFESPAN = timedelta(days=14)


    # Passwords

    # The number of iterations used when hashing a user's password. You might
    # want to configure this to a low number in local development environments
    # to ensure generating users from fixtures doesn't take too long. We don't
    # recommend less that 100,000 in production.
    USER_PASSWORD_HASH_ITERATIONS = 100000

    # The time before a reset password link for a user expires
    USER_PASSWORD_RESET_LIFESPAN = timedelta(days=14)

    # The set of rules for users when setting a password
    USER_PASSWORD_RULES = dict(
        min_length=10,
        max_length=128,
        min_lower=1,
        min_upper=1,
        min_digits=1,
        min_specials=1
    )


    # Failed sign-in attempts and lockouts

    # The cache used to store the number of failed attempts to sign-in for a
    # user identified (e.g an email).
    USER_FAILED_SIGN_IN_CACHE = SimpleCache()

    # The period of time a user is locked out for after too many failed
    # sign-in attempts.
    USER_FAILED_SIGN_IN_LOCKOUT = timedelta(minutes=30)

    # The window of time during which failed attempts are tallied before the
    # the tally is reset (the user can make `USER_MAX_FAILED_SIGN_IN_ATTEMPTS`
    # number of failed attempts within this window).
    USER_FAILED_SIGN_IN_WINDOW = timedelta(minutes=10)

    # The maximum number of times a user can fail to sign-in before being
    # locked out.
    USER_MAX_FAILED_SIGN_IN_ATTEMPTS = 3


    # MFA (Multi-factor authorization)

    # The cache used to store the number of failed attempts to authorize using
    # multi-factor authentication.
    USER_MFA_FAILED_AUTH_CACHE = SimpleCache()

    # The duration a user is locked out of MFA after failing to authorize,
    # this should be a short period (less than 30 seconds) set to throttle
    # the number of attempts that can be made for the time-based one time
    # password (TOTP).
    USER_MFA_FAILED_AUTH_LOCKOUT = timedelta(seconds=10)

    # The MFA provisioning issuer
    USER_MFA_ISSUER = 'NOT SET'

    # The number of times a user can incorrectly enter their time-based one
    # time password (TOPT) before we temporarily block their account from MFA.
    USER_MFA_MAX_FAILED_AUTH_ATTEMPTS = 3

    # The length of MFA recovery codes generated for a user
    USER_MFA_RECOVERY_CODE_LENGTH = 10

    # The number of MFA recovery codes to generate for a user
    USER_MFA_RECOVERY_CODES = 16

    # Flag indicating if MFA is required for users
    USER_MFA_REQUIRED = False

    # The cache used to store scoped session tokens
    USER_MFA_SCOPED_SESSION_CACHE = SimpleCache()

    # The period of time a scoped authorized session lasts (we recommended
    # under 30 minutes).
    USER_MFA_SCOPED_SESSION_LIFESPAN = timedelta(minutes=10)
