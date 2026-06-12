from __future__ import annotations

import json
import locale
import os
import random
import secrets
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None


@dataclass(slots=True)
class DeviceSession:
    instance_id: str
    device_id: str
    client_session_id: int
    device_type: str = "ANDROID"
    app_version: str = "26.17.1"
    build_number: int = 6712
    os_version: str = "Android 11"
    timezone: str = "Europe/Moscow"
    screen: str = "420dpi 420dpi 1080x2340"
    push_device_type: str = "GCM"
    arch: str = "arm64-v8a"
    locale: str = "ru"
    device_name: str = "TECNO MOBILE LIMITED TECNO LE7n"
    device_locale: str = "ru"
    token: str | None = None
    account_id: int | None = None
    phone: str | None = None

    @property
    def user_agent(self) -> dict[str, object]:
        return {
            "deviceType": self.device_type,
            "appVersion": self.app_version,
            "osVersion": self.os_version,
            "timezone": self.timezone,
            "screen": self.screen,
            "pushDeviceType": self.push_device_type,
            "arch": self.arch,
            "locale": self.locale,
            "buildNumber": self.build_number,
            "deviceName": self.device_name,
            "deviceLocale": self.device_locale,
        }

    @property
    def handshake_payload(self) -> dict[str, object]:
        return {
            "mt_instanceid": self.instance_id,
            "userAgent": self.user_agent,
            "clientSessionId": self.client_session_id,
            "deviceId": self.device_id,
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, ensure_ascii=False, indent=2)


def default_session_path(name: str) -> Path:
    base = Path(os.getenv("VKMAX_HOME", Path.home() / ".vkmax"))
    return base / f"{name}.json"


def load_or_create_session(path: str | Path) -> DeviceSession:
    path = Path(path)
    if path.exists():
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return _session_from_dict(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    session = create_device_session()
    session.save(path)
    return session


def _session_from_dict(data: dict[str, object]) -> DeviceSession:
    fields = {f for f in DeviceSession.__dataclass_fields__}
    filtered = {k: v for k, v in data.items() if k in fields}
    return DeviceSession(**filtered)


def create_device_session() -> DeviceSession:
    lang = (locale.getlocale()[0] or "ru_RU").split("_")[0] or "ru"
    return DeviceSession(
        instance_id=str(uuid.uuid4()),
        device_id=secrets.token_hex(8),
        client_session_id=random.SystemRandom().randint(1, 0x7FFFFFFF),
        timezone=_local_timezone(),
        locale=lang,
        device_locale=lang,
    )


def _local_timezone() -> str:
    if ZoneInfo is None:
        return "Europe/Moscow"
    try:
        return ZoneInfo(os.environ.get("TZ", "Europe/Moscow")).key
    except Exception:
        return "Europe/Moscow"
