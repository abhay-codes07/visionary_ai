class VisionaryError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class InvalidInputError(VisionaryError):
    def __init__(self, message: str = "Invalid input payload.") -> None:
        super().__init__(code="invalid_input", message=message, status_code=422)


class ServiceUnavailableError(VisionaryError):
    def __init__(self, message: str = "Service temporarily unavailable.") -> None:
        super().__init__(code="service_unavailable", message=message, status_code=503)
