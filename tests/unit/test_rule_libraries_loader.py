"""Authoring-layer rule loader tests (YAML/JSON parity)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "src"))
sys.path.append(str(ROOT))

from dq_contracts.serialization import to_canonical_json  # noqa: E402
from dq_core.models.data_quality_rule import ValidationRuleTemplate  # noqa: E402
from rule_libraries.loader import (  # noqa: E402
    canonical_json,
    load_rules_from_file,
    load_validation_rules,
)


def test_yaml_and_json_canonical_json_match(tmp_path: Path) -> None:
    """Authoring format (YAML vs JSON) should not change canonical JSON."""

    yaml_path = ROOT / "rule_libraries" / "validation_rules" / "example_validation.rules.yaml"
    yaml_rules = load_validation_rules(yaml_path)

    json_rule = {
        "rule_id": "dq-billing-net-balance",
        "name": "Net amount must equal gross minus tax",
        "dataset_type": "billing",
        "expression": "NetAmount == GrossAmount - TaxAmount",
        "severity": "hard",
        "description": "Prevents invoices where net totals drift from the gross/tax components.",
        "active_from": "2024-06-01",
    }
    json_path = tmp_path / "rule.json"
    json_path.write_text(json.dumps(json_rule), encoding="utf-8")

    json_rules = load_validation_rules(json_path)

    assert canonical_json(yaml_rules) == canonical_json(json_rules)  # legacy helper
    assert to_canonical_json(yaml_rules) == to_canonical_json(json_rules)  # registry helper


def test_multi_rule_yaml_list_supported(tmp_path: Path) -> None:
    """Multi-entry YAML lists should load all validation rules."""

    yaml_path = tmp_path / "multi.rules.yaml"
    yaml_path.write_text(
        "\n".join(
            [
                "- rule_id: rule-1",
                "  name: rule 1",
                "  dataset_type: billing",
                "  expression: Amount > 0",
                "  severity: hard",
                "- rule_id: rule-2",
                "  name: rule 2",
                "  dataset_type: billing",
                "  expression: Amount <= 1000",
                "  severity: soft",
            ]
        ),
        encoding="utf-8",
    )

    rules = load_rules_from_file(yaml_path, rule_type="validation")
    assert len(rules) == 2
    assert all(isinstance(rule, ValidationRuleTemplate) for rule in rules)
    ids = {rule.rule_id for rule in rules}
    assert ids == {"rule-1", "rule-2"}
