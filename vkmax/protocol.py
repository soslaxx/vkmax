from __future__ import annotations

import hashlib
import struct
from typing import Any

import msgpack

from .enums import API_VERSION, CMD_REQUEST
from .models import Packet

HEADER_SIZE = 10
MAX_DECOMPRESSED_SIZE = 16 * 1024 * 1024
MIN_COMPRESS_LEN = 32


def pack_packet(opcode: int, payload: dict[Any, Any] | None = None, *, seq: int = 0) -> bytes:
    raw = msgpack.packb(payload or {}, use_bin_type=True)
    body = raw
    flag = 0
    if len(raw) >= MIN_COMPRESS_LEN:
        compressed = _try_lz4_compress(raw)
        if compressed is not None and len(compressed) < len(raw):
            body = compressed
            flag = (len(raw) // len(body)) + 1
            if flag > 0xFF:
                flag = 0xFF
    packed_len = ((flag & 0xFF) << 24) | (len(body) & 0xFFFFFF)
    header = struct.pack(">BBHHI", API_VERSION, CMD_REQUEST, seq & 0xFFFF, opcode & 0xFFFF, packed_len)
    return header + body


def unpack_packet(data: bytes) -> Packet:
    if len(data) < HEADER_SIZE:
        raise ValueError("packet is shorter than header")
    api, cmd, seq, opcode, packed_len = struct.unpack(">BBHHI", data[:HEADER_SIZE])
    comp_flag = packed_len >> 24
    payload_len = packed_len & 0xFFFFFF
    end = HEADER_SIZE + payload_len
    if end > len(data):
        raise ValueError(f"packet payload length {payload_len} exceeds buffer")
    payload: Any = None
    if payload_len:
        body = data[HEADER_SIZE:end]
        if comp_flag:
            body = decompress_payload(body)
        payload = msgpack.unpackb(body, raw=False, strict_map_key=False)
    return Packet(api=api, cmd=cmd, seq=seq, opcode=opcode, payload=payload)


def packet_size_from_header(header: bytes) -> int:
    if len(header) != HEADER_SIZE:
        raise ValueError("header must be exactly 10 bytes")
    packed_len = struct.unpack(">I", header[6:10])[0]
    return HEADER_SIZE + (packed_len & 0xFFFFFF)


def decompress_payload(data: bytes) -> bytes:
    if data.startswith(b"\x28\xb5\x2f\xfd"):
        try:
            import zstandard as zstd
        except ImportError as exc:
            raise RuntimeError("zstandard is required to decode this packet") from exc
        return zstd.ZstdDecompressor(max_window_size=MAX_DECOMPRESSED_SIZE).decompress(data)
    if data.startswith(b"\x04\x22\x4d\x18"):
        try:
            import lz4.frame
        except ImportError as exc:
            raise RuntimeError("lz4 is required to decode this packet") from exc
        return lz4.frame.decompress(data)
    return _lz4_block_decompress(data, MAX_DECOMPRESSED_SIZE)


def _lz4_block_decompress(src: bytes, max_size: int = MAX_DECOMPRESSED_SIZE) -> bytes:
    out = bytearray()
    pos = 0
    src_len = len(src)
    while pos < src_len:
        token = src[pos]
        pos += 1
        literal_len = token >> 4
        if literal_len == 15:
            while pos < src_len:
                value = src[pos]
                pos += 1
                literal_len += value
                if value != 255:
                    break
        if literal_len:
            if len(out) + literal_len > max_size:
                raise ValueError("lz4 output exceeds max size")
            out.extend(src[pos:pos + literal_len])
            pos += literal_len
        if pos >= src_len:
            break
        if pos + 1 >= src_len:
            raise ValueError("unexpected end of lz4 input")
        offset = src[pos] | (src[pos + 1] << 8)
        pos += 2
        if offset == 0 or offset > len(out):
            raise ValueError("invalid lz4 offset")
        match_len = (token & 0x0F) + 4
        if (token & 0x0F) == 15:
            while pos < src_len:
                value = src[pos]
                pos += 1
                match_len += value
                if value != 255:
                    break
        if len(out) + match_len > max_size:
            raise ValueError("lz4 output exceeds max size")
        start = len(out) - offset
        for index in range(match_len):
            out.append(out[start + index])
    return bytes(out)


def _try_lz4_compress(raw: bytes) -> bytes | None:
    try:
        import lz4.block
    except ImportError:
        return None
    try:
        return lz4.block.compress(raw, store_size=False)
    except Exception:
        return None


def chat_cache_fingerprint(calls_seed: int, device_id: str) -> bytes:
    signature = bytes.fromhex("1684414033eb263e2c615f8b7df5ed8793850a07656304997fbf07e9e21e1e93")
    so_digest = bytes.fromhex("c77b89270f44bd26c218a946c18911f2b156312693ea00b419d169b71c1ed111")
    dex_digest = bytes.fromhex("490a2746c7ebbff050353c575a186ca65bc708f9b6e0c1329b59a3bfab6c3924")
    seed = struct.pack(">q", calls_seed)
    device = device_id.encode()
    return b"".join(hashlib.sha256(part + seed + device).digest() for part in (signature, so_digest, dex_digest))
