"""String case transformers."""

from __future__ import annotations

from toolkit.core.base_transformer import BaseTransformer
from toolkit.core.registry import TransformerRegistry


class TextToUpperTransformer(BaseTransformer):
    input_type = "text"
    output_type = "upper"

    def transform(self, data: str) -> str:
        return data.upper()


class TextToLowerTransformer(BaseTransformer):
    input_type = "text"
    output_type = "lower"

    def transform(self, data: str) -> str:
        return data.lower()


class TextToTitleTransformer(BaseTransformer):
    input_type = "text"
    output_type = "title"

    def transform(self, data: str) -> str:
        return data.title()


def register(registry: TransformerRegistry) -> None:
    registry.register_transformer(TextToUpperTransformer)
    registry.register_transformer(TextToLowerTransformer)
    registry.register_transformer(TextToTitleTransformer)
