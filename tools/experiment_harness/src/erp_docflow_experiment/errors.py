"""Typed failures exposed by the experiment harness."""


class HarnessError(Exception):
    """A fail-closed, user-actionable harness error."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.message = message
