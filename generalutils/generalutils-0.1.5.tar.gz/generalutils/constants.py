from dataclasses import dataclass

@dataclass
class HttpStatusCode:
    '''Data class for status code responses'''

    Ok: int = 200
    Created: int = 201
    NoContent: int = 204
    BadRequest: int = 400
    Unauthorized: int = 401
    Forbidden: int = 403
    NotFound: int = 404
    MethodNotAllowed: int = 405
    TooManyRequests: int = 429 
    InternalServerError: int = 500
    BadGateway: int = 502
    ServiceUnavailable: int = 503
    GatewayTimeout: int = 504
