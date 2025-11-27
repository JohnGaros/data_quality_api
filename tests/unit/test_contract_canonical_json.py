"""Canonical JSON for data contracts and rule templates."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "src"))

from dq_contracts import (  # noqa: E402
    DataContract,
    DatasetContract,
    Environment,
    RuleBinding,
    RuleBindingTargetScope,
    RuleTemplate,
    RuleType,
    to_canonical_json,
)
from dq_contracts.models import RuleParameter  # noqa: E402


def test_contract_serialization_to_canonical_json() -> None:
    """Data contracts should serialize consistently for DB and API use."""

    template = RuleTemplate(
        rule_template_id="tmpl-1",
        name="Net amount must match",
        rule_type=RuleType.VALIDATION,
        dataset_type="billing",
        version="1.0.0",
        severity="hard",
        source_module="dq_core",
        description="Net must equal gross minus tax.",
        default_parameters=[RuleParameter(name="tolerance", value=0.01)],
    )

    binding = RuleBinding(
        binding_id="bind-1",
        tenant_id="tnt-1",
        environment=Environment.DEV,
        rule_template_id="tmpl-1",
        rule_type=RuleType.VALIDATION,
        target_scope=RuleBindingTargetScope.DATASET,
        target_id="billing-dataset",
        parameters=[],
    )

    dataset_contract = DatasetContract(
        dataset_contract_id="billing-dataset",
        dataset_type="billing",
        tenant_id="tnt-1",
        environment=Environment.DEV,
        version="1.0.0",
    )

    contract = DataContract(
        contract_id="contract-1",
        tenant_id="tnt-1",
        environment=Environment.DEV,
        version="1.0.0",
        name="Billing Contract",
        description="Canonical billing dataset",
        datasets=[dataset_contract],
        rule_templates=[template],
        rule_bindings=[binding],
    )

    canonical = to_canonical_json(contract)

    assert canonical["contract_id"] == "contract-1"
    assert canonical["datasets"][0]["dataset_contract_id"] == "billing-dataset"
    assert canonical["rule_templates"][0]["rule_template_id"] == "tmpl-1"
    assert canonical["rule_bindings"][0]["binding_id"] == "bind-1"
    # Round-trip symmetry using JSON-friendly dump to match canonical serialization
    assert canonical == contract.model_dump(mode="json")


def test_canonical_json_list_support() -> None:
    """Lists of contracts should serialize to lists of dicts."""

    contract = DataContract(
        contract_id="contract-2",
        tenant_id="tnt-2",
        environment=Environment.TEST,
        version="2.0.0",
        name="Another",
        datasets=[],
        rule_templates=[],
        rule_bindings=[],
    )

    serialized = to_canonical_json([contract])
    assert isinstance(serialized, list)
    assert serialized[0]["contract_id"] == "contract-2"


def test_dataset_contract_catalog_entity_ids_backward_compatibility() -> None:
    """DatasetContract should accept single or multiple catalog entity IDs."""

    # Legacy single value should coerce to list via alias
    legacy_dataset = DatasetContract(
        dataset_contract_id="ds-legacy",
        dataset_type="legacy",
        tenant_id="tnt-legacy",
        environment=Environment.DEV,
        version="1.0.0",
        catalog_entity_id="customer_v1",
    )
    assert legacy_dataset.catalog_entity_ids == ["customer_v1"]
    legacy_dump = legacy_dataset.model_dump(mode="json")
    assert legacy_dump["catalog_entity_ids"] == ["customer_v1"]

    # New list usage should persist as-is
    modern_dataset = DatasetContract(
        dataset_contract_id="ds-modern",
        dataset_type="modern",
        tenant_id="tnt-modern",
        environment=Environment.DEV,
        version="1.0.0",
        catalog_entity_ids=["customer_v1", "account_v1"],
    )
    assert modern_dataset.catalog_entity_ids == ["customer_v1", "account_v1"]
    modern_dump = modern_dataset.model_dump(mode="json")
    assert modern_dump["catalog_entity_ids"] == ["customer_v1", "account_v1"]
