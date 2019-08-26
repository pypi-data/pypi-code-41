"""Constant value's that are used for the settings."""

__all__ = (
    "DEFAULTS",
    "LOADABLE",
    "NAMESPACE",
)

DEFAULTS = {
    # The token model to use. It is advised to use knox.models.AuthToken
    # because knox encrypts tokens and allows multiple tokens per user.
    "AUTH_TOKEN_MODEL": "authtoken.Token",

    # verification backends check if a user/token is verified with a one time
    # password.
    "DEFAULT_BACKEND_CLASS": "rest_multi_factor.backends.DefaultBackend",

    # The encryption settings points to the encryption handler for storing
    # sensitive values that need te be decrypted again.
    "DEFAULT_ENCRYPTION_CLASS":
        "rest_multi_factor.encryption.aes.AESEncryption",

    # The throttle class for the verify() view. It is crucial that if this
    # setting is changed that it is taught through because these throttles are
    # the only thing that protects the verification against brute force attacks
    "VERIFICATION_THROTTLING_CLASSES": (
        "rest_multi_factor.throttling.RecursiveDelayingThrottle",
    ),

    # The required number of verifications, default is one for two factor.
    #
    # XXX NOTE: MUST be one or more
    "REQUIRED_VERIFICATIONS": 1,

    # RFC validation checks if the security proposals of RFC 4226 and RFC 6238
    # are met. It is advised to keep this setting to True, at least in
    # development.
    "ALGORITHM_RFC_VALIDATION": True,

    # Throttle tryouts and timeout are value's that tell how many times a token
    # or secret may be tried to be verified and the time to wait. A minimal of
    # 30 seconds is advised against brute forcing TOTP token
    "VERIFICATION_THROTTLE_TRYOUTS": 5,
    "VERIFICATION_THROTTLE_TIMEOUT": "30s",
}

LOADABLE = [
    "DEFAULT_BACKEND_CLASS",
    "DEFAULT_ENCRYPTION_CLASS",
    "VERIFICATION_THROTTLING_CLASSES",
]

NAMESPACE = "REST_MULTI_FACTOR"
