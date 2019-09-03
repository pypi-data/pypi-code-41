class EcobeeError(Exception):
    """Base exception for all Ecobee exceptions."""

    pass


class AuthCodeEmptyError(EcobeeError):
    """Raised when tokens are requested but no authorization code is available."""

    pass


class ExpiredTokensError(EcobeeError):
    """Raised when tokens are expired."""

    pass


class RefreshTokenEmptyError(EcobeeError):
    """Raised when token refresh is requested but no refresh token is available."""

    pass
