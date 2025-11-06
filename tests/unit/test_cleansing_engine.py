import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_cleansing import (
    CleansingEngine,
    CleansingJob,
    CleansingJobStatus,
    CleansingRule,
    CleansingRuleLibrary,
    TransformationStep,
)
from dq_cleansing.models.cleansing_job import CleansingJobResult


def build_rule(version: str = "2024.06.01") -> CleansingRule:
    return CleansingRule(
        rule_id="billing-standardise",
        name="Billing standardisation",
        dataset_type="billing",
        version=version,
        transformations=[
            TransformationStep(
                type="standardize",
                target_fields=["Currency"],
                parameters={"format": "ISO-4217"},
            ),
            TransformationStep(
                type="fill_missing",
                target_fields=["CustomerId"],
                parameters={"default": "UNKNOWN"},
                severity="soft",
            ),
            TransformationStep(
                type="deduplicate",
                target_fields=["InvoiceNumber"],
                parameters={"keys": ["InvoiceNumber"]},
                severity="hard",
            ),
        ],
    )


def sample_dataset():
    return [
        {"InvoiceNumber": "INV-001", "Currency": "usd", "CustomerId": "C001"},
        {"InvoiceNumber": "INV-002", "Currency": "eur", "CustomerId": None},
        {"InvoiceNumber": "INV-002", "Currency": "eur", "CustomerId": None},
    ]


def test_engine_executes_transformations_in_order():
    engine = CleansingEngine()
    job = CleansingJob(
        job_id="cln-job-1",
        tenant_id="tenant-1",
        dataset_type="billing",
        rule_id="billing-standardise",
    )
    rule = build_rule()

    result, cleansed_dataset, warnings = engine.run(job, rule, sample_dataset())

    assert warnings == []
    assert isinstance(result, CleansingJobResult)
    assert result.status == CleansingJobStatus.SUCCEEDED
    assert result.before_counts["rows"] == 3
    assert result.after_counts["rows"] == 2  # duplicate removed
    assert cleansed_dataset[0]["Currency"] == "USD"
    assert cleansed_dataset[1]["CustomerId"] == "UNKNOWN"
    assert result.metrics["deduplicate"]["deduplicated"] == 1


def test_rule_library_returns_latest_version():
    library = CleansingRuleLibrary()
    library.upsert(build_rule(version="2024.06.01"))
    library.upsert(build_rule(version="2024.07.01"))

    rule = library.get("billing-standardise")
    assert rule is not None
    assert rule.version == "2024.07.01"

    specific = library.get("billing-standardise", version="2024.06.01")
    assert specific is not None
    assert specific.version == "2024.06.01"


def test_engine_raises_for_unknown_transformation():
    engine = CleansingEngine()
    job = CleansingJob(
        job_id="cln-job-2",
        tenant_id="tenant-1",
        dataset_type="billing",
        rule_id="billing-standardise",
    )
    rule = CleansingRule(
        rule_id="billing-standardise",
        name="Unsupported",
        dataset_type="billing",
        version="2024.06.01",
        transformations=[
            TransformationStep(type="unknown", target_fields=["InvoiceNumber"])
        ],
    )

    with pytest.raises(RuntimeError):
        engine.run(job, rule, sample_dataset())
