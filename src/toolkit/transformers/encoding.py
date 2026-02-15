"""Encoding and decoding transformers."""

from __future__ import annotations

import base64
from urllib.parse import quote, unquote

from toolkit.core.base_transformer import BaseTransformer
from toolkit.core.registry import TransformerRegistry


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
        return decoded.decode("utf-8")


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
    registry.register_transformer(TextToUrlEncodedTransformer)
    registry.register_transformer(UrlEncodedToTextTransformer)
