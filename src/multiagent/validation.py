"""Validation primitives for untrusted agent catalog definitions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


class CatalogError(KeyError):
    """Base error for catalog loading and lookup failures."""

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else self.__class__.__name__


class CatalogValidationError(CatalogError):
    """A catalog definition or reference violates the supported schema."""


_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_LIST_FIELDS = ("tags", "tools", "works_with", "recommended_patterns")
_MAPPING_FIELDS = (
    "parameters",
    "cost_profile",
    "orchestration",
    "safety",
    "observability",
    "outputs",
    "context",
    "protocols",
)
_RISK_LEVELS = {"none", "low", "medium", "high"}
_CONTEXT_LOADING = {"trigger", "progressive", "always"}


def is_safe_slug(value: str) -> bool:
    """Return whether a value is safe for catalog identifiers and filenames."""
    return bool(_SLUG.fullmatch(value))


def load_agent_data(path: Path) -> dict[str, Any]:
    """Parse and validate one agent YAML document."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise CatalogValidationError(f"{path}: invalid YAML: {error}") from error

    if not isinstance(data, dict):
        raise CatalogValidationError(f"{path}: YAML root must be a mapping")

    for field in ("name", "category"):
        value = data.get(field)
        if not isinstance(value, str) or not is_safe_slug(value):
            raise CatalogValidationError(
                f"{path}: {field} must be a lowercase kebab-case slug"
            )

    for field in ("description", "system_prompt"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise CatalogValidationError(f"{path}: {field} must be a non-empty string")

    version = data.get("version", "1.0")
    if not isinstance(version, (str, int, float)):
        raise CatalogValidationError(f"{path}: version must be a string or number")

    for field in _LIST_FIELDS:
        value = data.get(field, [])
        if not isinstance(value, list):
            raise CatalogValidationError(f"{path}: {field} must be a list")

    for field in _MAPPING_FIELDS:
        value = data.get(field, {})
        if not isinstance(value, dict):
            raise CatalogValidationError(f"{path}: {field} must be a mapping")

    _validate_string_list(path, "tags", data.get("tags", []))
    _validate_string_list(path, "works_with", data.get("works_with", []))

    for reference in data.get("works_with", []):
        parts = reference.split("/")
        if len(parts) != 2 or not all(_SLUG.fullmatch(part) for part in parts):
            raise CatalogValidationError(
                f"{path}: works_with entry '{reference}' must be category/name"
            )

    risk = data.get("safety", {}).get("side_effect_risk")
    if risk is not None and risk not in _RISK_LEVELS:
        raise CatalogValidationError(
            f"{path}: safety.side_effect_risk must be one of {sorted(_RISK_LEVELS)}"
        )

    review = data.get("safety", {}).get("requires_human_review")
    if review is not None and not isinstance(review, bool):
        raise CatalogValidationError(
            f"{path}: safety.requires_human_review must be a boolean"
        )

    loading = data.get("context", {}).get("loading")
    if loading is not None and loading not in _CONTEXT_LOADING:
        raise CatalogValidationError(
            f"{path}: context.loading must be one of {sorted(_CONTEXT_LOADING)}"
        )

    max_context = data.get("context", {}).get("max_context_tokens")
    if max_context is not None and (
        not isinstance(max_context, int) or isinstance(max_context, bool) or max_context <= 0
    ):
        raise CatalogValidationError(
            f"{path}: context.max_context_tokens must be a positive integer"
        )

    return data


def _validate_string_list(path: Path, field: str, values: list[Any]) -> None:
    if not all(isinstance(value, str) and value for value in values):
        raise CatalogValidationError(f"{path}: {field} entries must be non-empty strings")
