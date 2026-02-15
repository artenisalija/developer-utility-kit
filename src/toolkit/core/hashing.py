"""Hashing and checksum utilities."""

from __future__ import annotations

import binascii
import hashlib
import zlib
from dataclasses import dataclass


@dataclass(frozen=True)
class HashEntry:
    label: str
    value: str


def generate_hash_report(data: bytes, text_value: str | None = None) -> list[HashEntry]:
    """Generate a broad hash/checksum report.

    Some algorithms depend on OpenSSL/provider support and may be unavailable.
    """
    report: list[HashEntry] = []

    report.append(HashEntry("MD2 Hash Generator", _optional_hexdigest("md2", data)))
    report.append(HashEntry("MD4 Hash Generator", _optional_hexdigest("md4", data)))
    report.append(
        HashEntry("MD5 Hash Generator", hashlib.md5(data).hexdigest())  # noqa: S324  # nosec B324
    )
    report.append(HashEntry("NTLM Hash Generator", _ntlm_hash(text_value)))
    report.append(
        HashEntry("SHA1 Hash Generator", hashlib.sha1(data).hexdigest())  # noqa: S324  # nosec B324
    )
    report.append(HashEntry("SHA2 Hash Generator", hashlib.sha256(data).hexdigest()))
    report.append(HashEntry("SHA224 Hash Generator", hashlib.sha224(data).hexdigest()))
    report.append(HashEntry("SHA256 Hash Generator", hashlib.sha256(data).hexdigest()))
    report.append(HashEntry("SHA384 Hash Generator", hashlib.sha384(data).hexdigest()))
    report.append(HashEntry("SHA512 Hash Generator", hashlib.sha512(data).hexdigest()))
    report.append(HashEntry("SHA512/224 Hash Generator", _optional_hexdigest("sha512_224", data)))
    report.append(HashEntry("SHA512/256 Hash Generator", _optional_hexdigest("sha512_256", data)))
    report.append(HashEntry("SHA3-224 Hash Generator", hashlib.sha3_224(data).hexdigest()))
    report.append(HashEntry("SHA3-256 Hash Generator", hashlib.sha3_256(data).hexdigest()))
    report.append(HashEntry("SHA3-384 Hash Generator", hashlib.sha3_384(data).hexdigest()))
    report.append(HashEntry("SHA3-512 Hash Generator", hashlib.sha3_512(data).hexdigest()))
    report.append(HashEntry("CRC-16 Hash Generator", f"{binascii.crc_hqx(data, 0xFFFF):04x}"))
    report.append(HashEntry("CRC-32 Hash Generator", f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"))
    report.append(HashEntry("Shake-128 Hash Generator", hashlib.shake_128(data).hexdigest(32)))
    report.append(HashEntry("Shake-256 Hash Generator", hashlib.shake_256(data).hexdigest(64)))
    report.append(HashEntry("MD6 Hash Generator", _optional_hexdigest("md6", data)))
    report.append(HashEntry("Whirlpool Hash Generator", _optional_hexdigest("whirlpool", data)))
    report.append(HashEntry("Checksum Calculator", f"{sum(data) & 0xFFFFFFFF:08x}"))

    return report


def _optional_hexdigest(name: str, data: bytes) -> str:
    try:
        hasher = hashlib.new(name)
    except (ValueError, TypeError):
        return "Unavailable on this Python/OpenSSL build"
    hasher.update(data)
    return hasher.hexdigest()


def _ntlm_hash(text_value: str | None) -> str:
    if text_value is None:
        return "Unavailable: NTLM requires text input"
    try:
        hasher = hashlib.new("md4")  # noqa: S324  # nosec B324
    except (ValueError, TypeError):
        return "Unavailable on this Python/OpenSSL build (requires MD4)"
    hasher.update(text_value.encode("utf-16le"))  # pragma: no cover
    return hasher.hexdigest()  # pragma: no cover
