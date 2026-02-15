"""Encoding and decoding transformers."""

from __future__ import annotations

import base64
import re
from urllib.parse import quote, unquote

from toolkit.core.base_transformer import BaseTransformer
from toolkit.core.registry import TransformerRegistry

_BINARY_RE = re.compile(r"^[01\s]+$")
_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")


def _text_to_binary_bits(value: str) -> str:
    return " ".join(format(byte, "08b") for byte in value.encode("utf-8"))


def _binary_bits_to_bytes(value: str) -> bytes:
    compact = "".join(value.split())
    if not compact or not _BINARY_RE.match(value):
        raise ValueError("Invalid binary input")
    # Accept short bit-strings by left-padding to a full byte boundary.
    if len(compact) % 8 != 0:
        target_len = ((len(compact) + 7) // 8) * 8
        compact = compact.rjust(target_len, "0")
    try:
        return bytes(int(compact[i : i + 8], 2) for i in range(0, len(compact), 8))
    except ValueError as exc:
        raise ValueError("Invalid binary input") from exc


def _text_to_hex(value: str) -> str:
    return value.encode("utf-8").hex()


def _hex_to_bytes(value: str) -> bytes:
    compact = value.strip().replace(" ", "")
    if not compact or not _HEX_RE.match(compact):
        raise ValueError("Invalid hex input")
    if len(compact) % 2 != 0:
        raise ValueError("Hex input length must be even")
    try:
        return bytes.fromhex(compact)
    except ValueError as exc:
        raise ValueError("Invalid hex input") from exc


class TextToBase64Transformer(BaseTransformer):
    input_type = "text"
    output_type = "base64"

    def transform(self, data: str) -> str:
        return base64.b64encode(data.encode("utf-8")).decode("ascii")


class Base64ToTextTransformer(BaseTransformer):
    input_type = "base64"
    output_type = "text"

    def transform(self, data: str) -> str:
        try:
            decoded = base64.b64decode(data, validate=True)
        except Exception as exc:
            raise ValueError("Invalid base64 input") from exc
        try:
            return decoded.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Decoded base64 bytes are not valid UTF-8 text") from exc


class TextToBinaryTransformer(BaseTransformer):
    input_type = "text"
    output_type = "binary"

    def transform(self, data: str) -> str:
        return _text_to_binary_bits(data)


class BinaryToTextTransformer(BaseTransformer):
    input_type = "binary"
    output_type = "text"

    def transform(self, data: str) -> str:
        payload = _binary_bits_to_bytes(data)
        try:
            return payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Binary bytes are not valid UTF-8 text") from exc


class TextToHexTransformer(BaseTransformer):
    input_type = "text"
    output_type = "hex"

    def transform(self, data: str) -> str:
        return _text_to_hex(data)


class HexToTextTransformer(BaseTransformer):
    input_type = "hex"
    output_type = "text"

    def transform(self, data: str) -> str:
        payload = _hex_to_bytes(data)
        try:
            return payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Hex bytes are not valid UTF-8 text") from exc


class BinaryToHexTransformer(BaseTransformer):
    input_type = "binary"
    output_type = "hex"

    def transform(self, data: str) -> str:
        payload = _binary_bits_to_bytes(data)
        return payload.hex()


class HexToBinaryTransformer(BaseTransformer):
    input_type = "hex"
    output_type = "binary"

    def transform(self, data: str) -> str:
        payload = _hex_to_bytes(data)
        return " ".join(format(byte, "08b") for byte in payload)


class BinaryToBase64Transformer(BaseTransformer):
    input_type = "binary"
    output_type = "base64"

    def transform(self, data: str) -> str:
        payload = _binary_bits_to_bytes(data)
        return base64.b64encode(payload).decode("ascii")


class Base64ToBinaryTransformer(BaseTransformer):
    input_type = "base64"
    output_type = "binary"

    def transform(self, data: str) -> str:
        try:
            payload = base64.b64decode(data, validate=True)
        except Exception as exc:
            raise ValueError("Invalid base64 input") from exc
        return " ".join(format(byte, "08b") for byte in payload)


class TextToUrlEncodedTransformer(BaseTransformer):
    input_type = "text"
    output_type = "urlencode"

    def transform(self, data: str) -> str:
        return quote(data, safe="")


class UrlEncodedToTextTransformer(BaseTransformer):
    input_type = "urlencode"
    output_type = "text"

    def transform(self, data: str) -> str:
        return unquote(data)


def register(registry: TransformerRegistry) -> None:
    registry.register_transformer(TextToBase64Transformer)
    registry.register_transformer(Base64ToTextTransformer)
    registry.register_transformer(TextToBinaryTransformer)
    registry.register_transformer(BinaryToTextTransformer)
    registry.register_transformer(TextToHexTransformer)
    registry.register_transformer(HexToTextTransformer)
    registry.register_transformer(BinaryToHexTransformer)
    registry.register_transformer(HexToBinaryTransformer)
    registry.register_transformer(BinaryToBase64Transformer)
    registry.register_transformer(Base64ToBinaryTransformer)
    registry.register_transformer(TextToUrlEncodedTransformer)
    registry.register_transformer(UrlEncodedToTextTransformer)
