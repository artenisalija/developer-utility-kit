"""Transformer registry with module discovery."""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable
from typing import cast

from toolkit.core.base_transformer import BaseTransformer
from toolkit.transformers import optional_modules

Registrar = Callable[["TransformerRegistry"], None]


class TransformerRegistry:
    """Registry for direct input->output transformers."""

    def __init__(self) -> None:
        self._transformers: dict[tuple[str, str], type[BaseTransformer]] = {}
        self._load_errors: dict[str, str] = {}
        self._discover_builtin_transformers()
        self.load_optional_transformers()

    def register_transformer(self, transformer_cls: type[BaseTransformer]) -> None:
        key = (
            transformer_cls.input_type.lower().strip(),
            transformer_cls.output_type.lower().strip(),
        )
        self._transformers[key] = transformer_cls

    def transform(self, data: str, input_type: str, output_type: str) -> str:
        key = (input_type.lower().strip(), output_type.lower().strip())
        transformer_cls = self._transformers.get(key)
        if transformer_cls is None:
            raise ValueError(f"No transformer registered for {input_type} -> {output_type}")
        return transformer_cls().transform(data)

    def available_transformations(self, input_type: str | None = None) -> list[tuple[str, str]]:
        if input_type is None:
            return sorted(self._transformers.keys())
        normalized = input_type.lower().strip()
        return sorted([pair for pair in self._transformers if pair[0] == normalized])

    def load_errors(self) -> dict[str, str]:
        return dict(self._load_errors)

    def _discover_builtin_transformers(self) -> None:
        package_name = "toolkit.transformers"
        package = importlib.import_module(package_name)
        for module_info in pkgutil.iter_modules(package.__path__):
            module_name = module_info.name
            if module_name.startswith("_") or module_name in optional_modules.OPTIONAL_MODULES:
                continue
            full_name = f"{package_name}.{module_name}"
            module = importlib.import_module(full_name)
            register = cast(Registrar | None, getattr(module, "register", None))
            if register is not None:
                register(self)

    def load_optional_transformers(self) -> None:
        for module_name in optional_modules.OPTIONAL_MODULES:
            full_name = f"toolkit.transformers.{module_name}"
            try:
                module = importlib.import_module(full_name)
            except ModuleNotFoundError as exc:
                self._load_errors[full_name] = str(exc)
                continue
            register = cast(Registrar | None, getattr(module, "register", None))
            if register is not None:
                register(self)
