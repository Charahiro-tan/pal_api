class PalApiError(Exception):
    pass


class RequestError(PalApiError):
    pass


class UnAuthorizedError(PalApiError):
    pass
