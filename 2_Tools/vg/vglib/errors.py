"""Error types. Each carries the process exit code documented in cli.md."""


class VgError(Exception):
    exit_code = 1


class UsageError(VgError):
    """Bad input: missing file, invalid Shotlist, unknown target."""
    exit_code = 1


class Refused(VgError):
    """A safety rule said no: video gate, budget cap, low balance."""
    exit_code = 2


class ProviderError(VgError):
    """The provider rejected or failed the request."""
    exit_code = 3

    def __init__(self, message, code=None, payload=None):
        super().__init__(message)
        self.code = code
        self.payload = payload
