"""Tests for YAML/JSON rule loading across validation, cleansing, and profiling rules."""

import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "src"))

from dq_cleansing.models.cleansing_rule import CleansingRule  # noqa: E402
from dq_config.loader import (  # noqa: E402
    canonical_json,
    load_cleansing_rules,
    load_profiling_rules,
    load_rules_from_file,
    load_validation_rules,
)
from dq_core.models.data_quality_rule import (  # noqa: E402
    ProfilingRuleTemplate,
    ValidationRuleTemplate,
)


def test_validation_yaml_round_trips_to_json(tmp_path: Path) -> None:
    """YAML validation rules should load and produce canonical JSON identical to JSON inputs."""

    yaml_path = ROOT / "rule_libraries" / "validation_rules" / "example_validation.rules.yaml"
    rules_from_yaml = load_validation_rules(yaml_path)
    assert len(rules_from_yaml) == 1
    assert isinstance(rules_from_yaml[0], ValidationRuleTemplate)

    json_rule = {
        "rule_id": "dq-billing-net-balance",
        "name": "Net amount must equal gross minus tax",
        "dataset_type": "billing",
        "expression": "NetAmount == GrossAmount - TaxAmount",
        "severity": "hard",
        "description": "Prevents invoices where net totals drift from the gross/tax components.",
        "active_from": "2024-06-01",
    }
    json_path = tmp_path / "validation_rule.json"
    json_path.write_text(json.dumps(json_rule), encoding="utf-8")

    rules_from_json = load_validation_rules(json_path)
    assert canonical_json(rules_from_yaml) == canonical_json(rules_from_json)


def test_cleansing_yaml_loads_transformations() -> None:
    """Cleansing rule YAML should parse into a CleansingRule with ordered steps."""

    yaml_path = ROOT / "rule_libraries" / "cleansing_rules" / "example_cleansing.rules.yaml"
    rules = load_cleansing_rules(yaml_path)
    assert len(rules) == 1
    rule = rules[0]
    assert isinstance(rule, CleansingRule)
    assert rule.rule_id == "billing-standardise"
    assert len(rule.transformations) == 3
    assert rule.transformations[0].type == "standardize"


def test_profiling_yaml_loads_thresholds() -> None:
    """Profiling rule YAML should validate comparison operator and metric fields."""

    yaml_path = ROOT / "rule_libraries" / "profiling_rules" / "example_profiling.rules.yaml"
    rules = load_profiling_rules(yaml_path)
    assert len(rules) == 1
    rule = rules[0]
    assert isinstance(rule, ProfilingRuleTemplate)
    assert rule.profile_metric == "null_ratio"
    assert rule.comparison == "<="
    assert rule.threshold == pytest.approx(0.02)


def test_invalid_severity_rejected(tmp_path: Path) -> None:
    """Severity validation should reject unsupported values."""

    yaml_path = tmp_path / "bad_validation.yaml"
    yaml_path.write_text(
        "\n".join(
            [
                "rule_id: bad-rule",
                "name: Invalid severity",
                "dataset_type: billing",
                "expression: Amount > 0",
                "severity: critical",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_validation_rules(yaml_path)


def test_rule_type_inferred_from_path() -> None:
    """Loader should infer rule type when called without explicit rule_type."""

    yaml_path = ROOT / "rule_libraries" / "validation_rules" / "example_validation.rules.yaml"
    rules = load_rules_from_file(yaml_path)
    assert len(rules) == 1
    assert isinstance(rules[0], ValidationRuleTemplate)
