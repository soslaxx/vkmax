from .client import MaxClient
from .enums import Opcode
from .exceptions import (
    AuthError,
    FloodError,
    MaxError,
    NotConnected,
    PacketError,
    SessionExpired,
    TransportClosed,
    UploadError,
)
from .models import (
    Attachment,
    Chat,
    Contact,
    FileUpload,
    LoginResult,
    Message,
    Packet,
    ReactionCounter,
    ReactionInfo,
    UploadProgress,
    VerifyCodeResult,
)
from ._contacts import dm_chat_id
from ._notify import MUTE_FOREVER, MUTE_OFF
from .html_parse import parse_html
from .markdown import parse_markdown
from .privacy import (
    FamilyProtectionLevel,
    InactiveTtl,
    PrivacyAudience,
    PrivacyKey,
)
from .reactions import REACTION_ALIASES, resolve_reaction
from .session import DeviceSession, create_device_session, default_session_path, load_or_create_session

__version__ = "2.0.0"

__all__ = [
    "Attachment",
    "AuthError",
    "Chat",
    "Contact",
    "DeviceSession",
    "FamilyProtectionLevel",
    "FileUpload",
    "FloodError",
    "InactiveTtl",
    "LoginResult",
    "MUTE_FOREVER",
    "MUTE_OFF",
    "MaxClient",
    "MaxError",
    "Message",
    "NotConnected",
    "Opcode",
    "Packet",
    "PacketError",
    "PrivacyAudience",
    "PrivacyKey",
    "REACTION_ALIASES",
    "ReactionCounter",
    "ReactionInfo",
    "SessionExpired",
    "TransportClosed",
    "UploadError",
    "UploadProgress",
    "VerifyCodeResult",
    "__version__",
    "create_device_session",
    "default_session_path",
    "dm_chat_id",
    "parse_html",
    "parse_markdown",
    "load_or_create_session",
    "resolve_reaction",
]
