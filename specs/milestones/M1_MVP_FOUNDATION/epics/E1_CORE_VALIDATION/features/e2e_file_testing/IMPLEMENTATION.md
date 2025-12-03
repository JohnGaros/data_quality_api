# End-to-End Excel/CSV Testing Implementation Guide

**Version:** 1.0
**Last Updated:** 2025-11-27
**Status:** Ready for Implementation

## Quick Reference: Your Questions Answered

### Where do files go?

**Input Files:**

- Location: `tests/fixtures/datasets/{domain}/`
- Example: `tests/fixtures/datasets/billing/billing_valid.csv`
- Small files (3-5 rows), version controlled

**Output Files:**

- Location: `tests/fixtures/outputs/{type}/`
- Cleansed: `outputs/cleansed/{job_id}_cleansed.csv`
- Rejected: `outputs/rejected/{job_id}_rejected.csv`
- Profiling: `outputs/profiling/{job_id}_profile.json`
- Validation: `outputs/validation/{job_id}_validation.json`
- All outputs gitignored (ephemeral artifacts)

### How are tenants identified?

Hardcoded test fixtures - no authentication needed:

```python
TENANT_ACME = {"tenant_id": "tenant-acme", "environment": "dev"}

job = CleansingJob(
    job_id="cln-job-1",
    tenant_id=TENANT_ACME["tenant_id"],
    dataset_type="billing",
    rule_id="billing-standardise",
)
```

### How do I retrieve outputs?

**Manual:** Open CSV in Excel, JSON with `jq`
**Programmatic:** `load_csv_to_dict_list(path)`
**Tests:** `assert len(cleansed_dataset) == 3`

---

## Architecture Context

This feature implements end-to-end testing workflows described in:

- **Primary:** `docs/ARCHITECTURE.md` - Testing Strategy & Integration Patterns
- **Contracts:** `docs/CONTRACT_DRIVEN_ARCHITECTURE.md` - CDA principles (engines consume contracts)
- **Metadata:** `docs/METADATA_LAYER_SPEC.md` - Job lineage and profiling snapshots
- **Security:** `docs/SECURITY_GUIDE.md` - Tenant isolation patterns

**Modules touched:**

- `src/dq_cleansing/` - CleansingEngine, CleansingJob, CleansingRule
- `src/dq_profiling/` - ProfilingEngine, ProfilingJob, ProfilingSnapshot
- `tests/fixtures/` - File loaders, savers, tenant fixtures (NEW)
- `tests/integration/` - End-to-end workflow tests (NEW)

**Key architectural patterns validated:**

1. List[Dict] as canonical dataset format (not DataFrames)
2. Tenant-scoped job execution (tenant_id + environment)
3. Cleansing → Profiling → Validation pipeline
4. File-based output inspection (CSV/JSON for manual verification)

---

## Architecture

### Key Insight

Engines work with `List[Dict[str, Any]]`, NOT DataFrames:

- `CleansingEngine.run()` → `Dataset = List[Dict[str, Any]]`
- `ProfilingEngine.profile()` → `Iterable[Dict[str, Any]]`
- `PandasExecutionEngine` not wired (raises `NotImplementedError`)

**Solution:** Adapter functions (pandas ↔ dicts ↔ engines)

### Data Flow

```
CSV File → load_csv_to_dict_list() → List[Dict]
                                        ↓
                              CleansingEngine.run()
                                        ↓
                    Cleansed + Rejected (List[Dict])
                                        ↓
                         save_cleansed_dataset()
                                        ↓
                            CSV Files (outputs/)
                                        ↓
                           ProfilingEngine.profile()
                                        ↓
                              ProfilingSnapshot
                                        ↓
                        save_profiling_snapshot()
                                        ↓
                            JSON File (outputs/)
```

---

## Phase 1: File Structure & Sample Data

### Create Directories

```bash
mkdir -p tests/fixtures/datasets/billing
mkdir -p tests/fixtures/outputs/{cleansed,rejected,profiling,validation}
```

### Sample CSV: billing_valid.csv

**File:** `tests/fixtures/datasets/billing/billing_valid.csv`

```csv
InvoiceNumber,Currency,CustomerId,Amount,GrossAmount,TaxAmount,NetAmount
INV-001,usd,C001,1000.00,1200.00,200.00,1000.00
INV-002,eur,C002,2500.00,3000.00,500.00,2500.00
INV-003,gbp,C003,750.00,900.00,150.00,750.00
```

Purpose: Clean data where all transformations succeed

### Sample CSV: billing_duplicates.csv

**File:** `tests/fixtures/datasets/billing/billing_duplicates.csv`

```csv
InvoiceNumber,Currency,CustomerId,Amount
INV-001,usd,C001,1000.00
INV-001,eur,C002,1500.00
INV-003,gbp,C003,750.00
```

Purpose: Test deduplication (INV-001 appears twice)

### Sample CSV: billing_missing_customer.csv

**File:** `tests/fixtures/datasets/billing/billing_missing_customer.csv`

```csv
InvoiceNumber,Currency,CustomerId,Amount
INV-001,usd,C001,1000.00
INV-002,eur,,2500.00
INV-003,gbp,,750.00
```

Purpose: Test fill_missing (CustomerId null in rows 2-3)

### Add .gitignore

**File:** `tests/fixtures/.gitignore`

```
outputs/
```

---

## Phase 2: File Loaders

**File:** `tests/fixtures/file_loaders.py`

```python
"""File loaders for Excel/CSV → list-of-dicts conversion."""

from pathlib import Path
from typing import Any, Dict, List
import pandas as pd


def load_csv_to_dict_list(file_path: Path) -> List[Dict[str, Any]]:
    """Load CSV file into list of dictionaries (engine format)."""
    df = pd.read_csv(file_path)
    df = df.where(pd.notna(df), None)  # Replace NaN with None
    return df.to_dict(orient="records")


def load_excel_to_dict_list(
    file_path: Path,
    sheet_name: str | int = 0
) -> List[Dict[str, Any]]:
    """Load Excel file into list of dictionaries."""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.where(pd.notna(df), None)
    return df.to_dict(orient="records")
```

---

## Phase 3: File Savers

**File:** `tests/fixtures/file_savers.py`

```python
"""File savers for results → CSV/JSON conversion."""

from pathlib import Path
from typing import Any, Dict, List
import json
import pandas as pd

from dq_profiling.models.profiling_snapshot import ProfilingSnapshot

OUTPUTS_DIR = Path(__file__).parent / "outputs"


def save_cleansed_dataset(job_id: str, dataset: List[Dict[str, Any]]) -> Path:
    """Save cleansed dataset as CSV."""
    output_path = OUTPUTS_DIR / "cleansed" / f"{job_id}_cleansed.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(dataset)
    df.to_csv(output_path, index=False)
    return output_path


def save_rejected_rows(job_id: str, rejected: List[Dict[str, Any]]) -> Path:
    """Save rejected rows as CSV."""
    output_path = OUTPUTS_DIR / "rejected" / f"{job_id}_rejected.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rejected:
        output_path.write_text("# No rejected rows\n")
    else:
        df = pd.DataFrame(rejected)
        df.to_csv(output_path, index=False)

    return output_path


def save_profiling_snapshot(job_id: str, snapshot: ProfilingSnapshot) -> Path:
    """Save profiling snapshot as JSON."""
    output_path = OUTPUTS_DIR / "profiling" / f"{job_id}_profile.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(snapshot.json(indent=2))
    return output_path


def save_validation_result(job_id: str, result: Dict[str, Any]) -> Path:
    """Save validation result as JSON."""
    output_path = OUTPUTS_DIR / "validation" / f"{job_id}_validation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    return output_path
```

---

## Phase 4: Test Fixtures

**File:** `tests/fixtures/tenant_fixtures.py`

```python
"""Reusable tenant fixtures for testing."""

from pathlib import Path


TENANT_ACME = {"tenant_id": "tenant-acme", "environment": "dev"}
TENANT_BETA = {"tenant_id": "tenant-beta", "environment": "test"}


FIXTURES_DIR = Path(__file__).parent
DATASETS_DIR = FIXTURES_DIR / "datasets"
OUTPUTS_DIR = FIXTURES_DIR / "outputs"


def get_dataset_path(domain: str, filename: str) -> Path:
    """Get path to a test dataset file."""
    return DATASETS_DIR / domain / filename
```

---

## Phase 5: End-to-End Integration Test

**File:** `tests/integration/test_e2e_file_workflow.py`

```python
"""End-to-end test: CSV file → cleansing → profiling → outputs."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from fixtures.file_loaders import load_csv_to_dict_list
from fixtures.file_savers import (
    save_cleansed_dataset,
    save_rejected_rows,
    save_profiling_snapshot,
)
from fixtures.tenant_fixtures import TENANT_ACME, get_dataset_path

from dq_cleansing import (
    CleansingEngine,
    CleansingJob,
    CleansingRule,
    TransformationStep,
)
from dq_profiling import ProfilingEngine, ProfilingJob


def test_billing_valid_e2e_workflow():
    """Test complete workflow: CSV → cleansing → profiling → saved outputs."""

    # Load CSV file
    csv_path = get_dataset_path("billing", "billing_valid.csv")
    dataset = load_csv_to_dict_list(csv_path)

    assert len(dataset) == 3
    assert dataset[0]["InvoiceNumber"] == "INV-001"

    # Define cleansing rule
    rule = CleansingRule(
        rule_id="billing-standardise",
        name="Billing standardisation",
        dataset_type="billing",
        version="2024.06.01",
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
            ),
            TransformationStep(
                type="deduplicate",
                target_fields=["InvoiceNumber"],
                parameters={"keys": ["InvoiceNumber"]},
            ),
        ],
    )

    # Run cleansing
    job = CleansingJob(
        job_id="e2e-billing-001",
        tenant_id=TENANT_ACME["tenant_id"],
        dataset_type="billing",
        rule_id="billing-standardise",
    )

    engine = CleansingEngine()
    result, cleansed_dataset, warnings = engine.run(job, rule, dataset)

    # Save cleansing outputs
    cleansed_path = save_cleansed_dataset(job.job_id, cleansed_dataset)

    rejected = []
    for step_type, step_metrics in result.metrics.items():
        if isinstance(step_metrics, dict) and "rejected" in step_metrics:
            rejected.extend(step_metrics["rejected"])

    rejected_path = save_rejected_rows(job.job_id, rejected)

    # Run profiling
    profiling_job = ProfilingJob(
        job_id=f"prof-{job.job_id}",
        tenant_id=TENANT_ACME["tenant_id"],
        dataset_type="billing",
        metadata={"input": "cleansed"},
    )

    profiling_engine = ProfilingEngine(sample_size=5, top_frequencies=5)
    profiling_result = profiling_engine.profile(profiling_job, cleansed_dataset)

    # Save profiling outputs
    profile_path = save_profiling_snapshot(job.job_id, profiling_result.snapshot)

    # Assertions
    assert result.status.value == "succeeded"
    assert result.after_counts["rows"] == 3
    assert cleansed_dataset[0]["Currency"] == "USD"  # Standardized
    assert profiling_result.snapshot.record_count == 3
    assert "Amount" in profiling_result.snapshot.field_stats

    assert cleansed_path.exists()
    assert profile_path.exists()

    print(f"\n✓ Cleansed dataset saved: {cleansed_path}")
    print(f"✓ Profiling snapshot saved: {profile_path}")


def test_billing_duplicates_workflow():
    """Test workflow with duplicate invoices (should be rejected)."""

    csv_path = get_dataset_path("billing", "billing_duplicates.csv")
    dataset = load_csv_to_dict_list(csv_path)

    rule = CleansingRule(
        rule_id="billing-standardise",
        name="Billing standardisation",
        dataset_type="billing",
        version="2024.06.01",
        transformations=[
            TransformationStep(
                type="deduplicate",
                target_fields=["InvoiceNumber"],
                parameters={"keys": ["InvoiceNumber"]},
            ),
        ],
    )

    job = CleansingJob(
        job_id="e2e-billing-002",
        tenant_id=TENANT_ACME["tenant_id"],
        dataset_type="billing",
        rule_id="billing-standardise",
    )

    engine = CleansingEngine()
    result, cleansed_dataset, warnings = engine.run(job, rule, dataset)

    save_cleansed_dataset(job.job_id, cleansed_dataset)
    rejected = result.metrics.get("deduplicate", {}).get("rejected", [])
    save_rejected_rows(job.job_id, rejected)

    assert len(cleansed_dataset) < len(dataset)
    assert result.after_counts["rejected"] > 0

    print(f"\n✓ Deduplication test passed: {len(rejected)} row(s) rejected")


def test_billing_missing_customer_workflow():
    """Test workflow with missing CustomerId (should be filled)."""

    csv_path = get_dataset_path("billing", "billing_missing_customer.csv")
    dataset = load_csv_to_dict_list(csv_path)

    assert dataset[1]["CustomerId"] is None
    assert dataset[2]["CustomerId"] is None

    rule = CleansingRule(
        rule_id="billing-standardise",
        name="Billing standardisation",
        dataset_type="billing",
        version="2024.06.01",
        transformations=[
            TransformationStep(
                type="fill_missing",
                target_fields=["CustomerId"],
                parameters={"default": "UNKNOWN"},
            ),
        ],
    )

    job = CleansingJob(
        job_id="e2e-billing-003",
        tenant_id=TENANT_ACME["tenant_id"],
        dataset_type="billing",
        rule_id="billing-standardise",
    )

    engine = CleansingEngine()
    result, cleansed_dataset, warnings = engine.run(job, rule, dataset)

    save_cleansed_dataset(job.job_id, cleansed_dataset)

    assert cleansed_dataset[1]["CustomerId"] == "UNKNOWN"
    assert cleansed_dataset[2]["CustomerId"] == "UNKNOWN"

    print(f"\n✓ Fill missing test passed: null CustomerIds replaced")
```

---

## Phase 6: Run and Verify

### Run Tests

```bash
pytest tests/integration/test_e2e_file_workflow.py -v
pytest tests/integration/test_e2e_file_workflow.py -v -s  # Show prints
```

### Verify Outputs

```bash
# Cleansed CSV
cat tests/fixtures/outputs/cleansed/e2e-billing-001_cleansed.csv

# Profiling JSON
cat tests/fixtures/outputs/profiling/e2e-billing-001_profile.json | jq

# List all outputs
find tests/fixtures/outputs -type f
```

---

## Phase 7: Documentation

**File:** `tests/fixtures/README.md`

```markdown
# Test Fixtures

Sample datasets and test outputs for end-to-end integration testing.

## Directory Structure
```

tests/fixtures/
├── datasets/ # Sample CSV/Excel files
│ └── billing/
│ ├── billing_valid.csv
│ ├── billing_duplicates.csv
│ └── billing_missing_customer.csv
├── outputs/ # Generated (gitignored)
│ ├── cleansed/
│ ├── rejected/
│ ├── profiling/
│ └── validation/
├── file_loaders.py
├── file_savers.py
├── tenant_fixtures.py
└── README.md

````

## Sample Datasets

| File | Rows | Description |
|------|------|-------------|
| `billing_valid.csv` | 3 | Clean data |
| `billing_duplicates.csv` | 3 | Duplicate INV-001 |
| `billing_missing_customer.csv` | 3 | Null CustomerId |

## Running Tests

```bash
pytest tests/integration/test_e2e_file_workflow.py -v
````

## Inspecting Outputs

```bash
# CSV
cat tests/fixtures/outputs/cleansed/e2e-billing-001_cleansed.csv

# JSON
cat tests/fixtures/outputs/profiling/e2e-billing-001_profile.json | jq
```

````

---

## Files to Create

### New Files (8)

1. `tests/fixtures/datasets/billing/billing_valid.csv`
2. `tests/fixtures/datasets/billing/billing_duplicates.csv`
3. `tests/fixtures/datasets/billing/billing_missing_customer.csv`
4. `tests/fixtures/file_loaders.py`
5. `tests/fixtures/file_savers.py`
6. `tests/fixtures/tenant_fixtures.py`
7. `tests/integration/test_e2e_file_workflow.py`
8. `tests/fixtures/README.md`

### Directories (5)

```bash
tests/fixtures/datasets/billing/
tests/fixtures/outputs/cleansed/
tests/fixtures/outputs/rejected/
tests/fixtures/outputs/profiling/
tests/fixtures/outputs/validation/
````

---

## Success Criteria

✅ Run tests: `pytest tests/integration/test_e2e_file_workflow.py -v`
✅ Inspect CSV: `cat outputs/cleansed/e2e-billing-001_cleansed.csv`
✅ Inspect JSON: `cat outputs/profiling/e2e-billing-001_profile.json | jq`
✅ Understand tenant flow (hardcoded strings, no auth)
✅ Understand output retrieval (filesystem, manual + programmatic)

---

## Next Steps

After basic flow works, extend with:

1. Validation engine integration
2. API upload endpoints
3. More sample domains
4. Excel file support
5. Database persistence
6. Azure Blob integration
