from __future__ import annotations

from typing import Any


class MaxError(Exception):
    pass


class TransportClosed(MaxError):
    pass


class NotConnected(MaxError):
    pass


class PacketError(MaxError):
    def __init__(self, message: str, *, error_key: str | None = None, payload: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_key = error_key
        self.payload = payload

    def __repr__(self) -> str:
        return f"PacketError({self.message!r}, error_key={self.error_key!r})"


class SessionExpired(PacketError):
    pass


class AuthError(PacketError):
    pass


class FloodError(PacketError):
    pass


class UploadError(MaxError):
    pass
