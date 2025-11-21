"""File-based rule loader for the authoring layer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple, Type, TypeVar, Union

import yaml
from pydantic import BaseModel

from dq_cleansing.models.cleansing_rule import CleansingRule
from dq_contracts.models import RuleType
from dq_contracts.serialization import to_canonical_json
from dq_core.models.data_quality_rule import ProfilingRuleTemplate, ValidationRuleTemplate

RuleModel = TypeVar("RuleModel", bound=BaseModel)

_MODEL_BY_RULE_TYPE: dict[RuleType, Type[BaseModel]] = {
    RuleType.VALIDATION: ValidationRuleTemplate,
    RuleType.CLEANSING: CleansingRule,
    RuleType.PROFILING: ProfilingRuleTemplate,
}


def canonical_json(rules: Union[BaseModel, Iterable[BaseModel]]) -> Union[dict[str, Any], List[dict[str, Any]]]:
    """Produce canonical JSON dictionaries from rule models (for DB/API/exports)."""
    return to_canonical_json(rules)


def _ensure_list(raw: Any) -> List[Any]:
    """Normalise raw data into a list for consistent parsing."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    return [raw]


def _model_for_type(rule_type: Union[str, RuleType]) -> Type[BaseModel]:
    """Resolve the model class for a given rule family."""
    try:
        rule_enum = RuleType(rule_type)
    except Exception as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Unsupported rule type: {rule_type}") from exc

    model_cls = _MODEL_BY_RULE_TYPE.get(rule_enum)
    if not model_cls:
        raise ValueError(f"Unsupported rule type: {rule_enum.value}")
    return model_cls


def _detect_rule_type_from_path(path: Path) -> Optional[RuleType]:
    """Infer rule type based on parent folder naming conventions."""

    parts = {p.name.lower() for p in path.parents if p.name}
    mapping = {
        "validation_rules": RuleType.VALIDATION,
        "profiling_rules": RuleType.PROFILING,
        "cleansing_rules": RuleType.CLEANSING,
        "dq_rules": None,  # Legacy folder; cannot infer specific type reliably.
    }
    for folder, detected in mapping.items():
        if folder in parts and detected:
            return detected
    return None


def parse_yaml_rules(path: Union[str, Path], model_cls: Type[RuleModel]) -> List[RuleModel]:
    """Load YAML rule definitions into strongly typed models."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    rules: List[RuleModel] = []
    for item in _ensure_list(data):
        if not isinstance(item, dict):
            raise ValueError("Each YAML rule entry must be a mapping/object")
        rules.append(model_cls(**item))
    return rules


def parse_json_rules(path: Union[str, Path], model_cls: Type[RuleModel]) -> List[RuleModel]:
    """Load JSON rule definitions into strongly typed models."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    rules: List[RuleModel] = []
    for item in _ensure_list(data):
        if not isinstance(item, dict):
            raise ValueError("Each JSON rule entry must be an object")
        rules.append(model_cls(**item))
    return rules


def parse_excel_rules(path: Union[str, Path], model_cls: Type[RuleModel]) -> List[RuleModel]:
    """Load Excel rule definitions into strongly typed models."""
    try:
        import pandas as pd  # type: ignore
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ImportError("pandas is required to parse Excel rule templates") from exc

    try:
        dataframe = pd.read_excel(path)  # type: ignore[call-arg]
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ImportError("openpyxl or equivalent Excel engine is required by pandas.read_excel") from exc

    records = dataframe.replace({pd.NA: None}).to_dict(orient="records")  # type: ignore[attr-defined]
    rules: List[RuleModel] = []
    for item in _ensure_list(records):
        rules.append(model_cls(**item))
    return rules


def load_rules_from_file(path: Union[str, Path], rule_type: Optional[Union[str, RuleType]] = None) -> List[BaseModel]:
    """Generic entry point that detects file type and returns validated rule models."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    detected_type = rule_type or _detect_rule_type_from_path(path)
    if not detected_type:
        raise ValueError("rule_type must be provided or inferable from the path")

    model_cls = _model_for_type(detected_type)
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return parse_yaml_rules(path, model_cls)
    if suffix == ".json":
        return parse_json_rules(path, model_cls)
    if suffix == ".xlsx":
        return parse_excel_rules(path, model_cls)

    raise ValueError(f"Unsupported file extension for rule loading: {suffix}")


def load_validation_rules(path: Union[str, Path]) -> List[ValidationRuleTemplate]:
    """Typed entry point for validation rules."""

    rules = load_rules_from_file(path, RuleType.VALIDATION)
    return [rule for rule in rules if isinstance(rule, ValidationRuleTemplate)]


def load_profiling_rules(path: Union[str, Path]) -> List[ProfilingRuleTemplate]:
    """Typed entry point for profiling rules."""

    rules = load_rules_from_file(path, RuleType.PROFILING)
    return [rule for rule in rules if isinstance(rule, ProfilingRuleTemplate)]


def load_cleansing_rules(path: Union[str, Path]) -> List[CleansingRule]:
    """Typed entry point for cleansing rules."""

    rules = load_rules_from_file(path, RuleType.CLEANSING)
    return [rule for rule in rules if isinstance(rule, CleansingRule)]


__all__: Tuple[str, ...] = (
    "canonical_json",
    "load_cleansing_rules",
    "load_rules_from_file",
    "load_profiling_rules",
    "load_validation_rules",
    "parse_excel_rules",
    "parse_json_rules",
    "parse_yaml_rules",
)
