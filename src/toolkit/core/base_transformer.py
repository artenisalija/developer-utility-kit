"""Base interfaces for transformers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTransformer(ABC):
    """Base class for one-step format transformations."""

    input_type: str
    output_type: str

    @abstractmethod
    def transform(self, data: str) -> str:
        """Transform data from input_type to output_type."""
