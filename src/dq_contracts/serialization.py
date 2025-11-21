"""Canonical JSON serialization helpers for contract and rule models."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any, Union

from pydantic import BaseModel


def _model_to_dict(model: BaseModel) -> dict[str, Any]:
    """Normalise a Pydantic model into a plain dict."""
    if hasattr(model, "model_dump_json"):
        return json.loads(model.model_dump_json())
    return json.loads(model.json())


def to_canonical_json(models: Union[BaseModel, Iterable[BaseModel]]) -> Union[dict[str, Any], list[dict[str, Any]]]:
    """
    Convert a model or iterable of models into canonical JSON-ready dictionaries.

    This is the single path used for:
    - Registry persistence (JSONB in Postgres)
    - API responses
    - Downstream services (validation, cleansing, profiling)
    - Metadata exports
    """

    if isinstance(models, BaseModel):
        return _model_to_dict(models)

    if isinstance(models, Iterable):
        return [_model_to_dict(model) for model in models]

    raise TypeError("to_canonical_json expects a Pydantic model or an iterable of models")


__all__ = ["to_canonical_json"]
