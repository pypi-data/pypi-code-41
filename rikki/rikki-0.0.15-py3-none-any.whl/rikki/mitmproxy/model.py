from typing import Dict, Optional


class Request:
    def __init__(
            self,
            host: Optional[str] = None,
            params: Optional[Dict[str, object]] = None,
            headers: Optional[Dict[str, str]] = None,
            content: Optional[str] = None
    ) -> None:
        super().__init__()
        self.host: Optional[str] = host
        self.params: Optional[Dict[str, object]] = params
        self.headers: Optional[Dict[str, str]] = headers
        self.content: Optional[str] = content


class Response:
    def __init__(
            self,
            headers: Optional[Dict[str, str]] = None,
            content: Optional[str] = None,
            code: Optional[int] = None
    ) -> None:
        super().__init__()
        self.headers: Optional[Dict[str, str]] = headers
        self.content: Optional[str] = content
        self.code: Optional[int] = code
