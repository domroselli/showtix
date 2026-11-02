"""Domain errors. main.py turns these into HTTP responses."""


class ShowTixError(Exception):
    status_code = 400


class NotFound(ShowTixError):
    status_code = 404


class BadRequest(ShowTixError):
    status_code = 400


class Conflict(ShowTixError):
    status_code = 409


class ServiceUnavailable(ShowTixError):
    status_code = 503
