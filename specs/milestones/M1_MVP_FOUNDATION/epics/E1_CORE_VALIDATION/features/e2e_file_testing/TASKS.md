# End-to-End Excel/CSV Testing - Task List

**Version:** 1.0
**Last Updated:** 2025-11-27

Use this checklist to track implementation progress. Check off each task as you complete it.

---

## Phase 1: File Structure & Sample Data

### Directories

- [ ] Create `tests/fixtures/datasets/billing/`
- [ ] Create `tests/fixtures/datasets/customer/` (future)
- [ ] Create `tests/fixtures/outputs/cleansed/`
- [ ] Create `tests/fixtures/outputs/rejected/`
- [ ] Create `tests/fixtures/outputs/profiling/`
- [ ] Create `tests/fixtures/outputs/validation/`

**Quick command:**
```bash
mkdir -p tests/fixtures/datasets/{billing,customer}
mkdir -p tests/fixtures/outputs/{cleansed,rejected,profiling,validation}
```

### Sample CSV Files

- [ ] Create `tests/fixtures/datasets/billing/billing_valid.csv`
  - 3 rows, clean data
  - Fields: `InvoiceNumber`, `Currency`, `CustomerId`, `Amount`, `GrossAmount`, `TaxAmount`, `NetAmount`

- [ ] Create `tests/fixtures/datasets/billing/billing_duplicates.csv`
  - 3 rows with duplicate `InvoiceNumber` (INV-001 appears twice)
  - Fields: `InvoiceNumber`, `Currency`, `CustomerId`, `Amount`

- [ ] Create `tests/fixtures/datasets/billing/billing_missing_customer.csv`
  - 3 rows with null `CustomerId` in rows 2-3
  - Fields: `InvoiceNumber`, `Currency`, `CustomerId`, `Amount`

### Git Configuration

- [ ] Create `tests/fixtures/.gitignore` with `outputs/`

---

## Phase 2: File Loaders

- [ ] Create `tests/fixtures/file_loaders.py`
  - [ ] Implement `load_csv_to_dict_list(file_path: Path) -> List[Dict[str, Any]]`
    - Use `pd.read_csv()`
    - Replace NaN with None: `df.where(pd.notna(df), None)`
    - Convert to dict list: `df.to_dict(orient="records")`

  - [ ] Implement `load_excel_to_dict_list(file_path: Path, sheet_name=0) -> List[Dict[str, Any]]`
    - Use `pd.read_excel()`
    - Same NaN replacement and conversion

- [ ] Test loaders in Python REPL:
  ```python
  from fixtures.file_loaders import load_csv_to_dict_list
  data = load_csv_to_dict_list(Path("tests/fixtures/datasets/billing/billing_valid.csv"))
  print(data[0])  # Should show dict with InvoiceNumber, Currency, etc.
  ```

---

## Phase 3: File Savers

- [ ] Create `tests/fixtures/file_savers.py`
  - [ ] Define `OUTPUTS_DIR = Path(__file__).parent / "outputs"`

  - [ ] Implement `save_cleansed_dataset(job_id: str, dataset: List[Dict]) -> Path`
    - Create output path: `OUTPUTS_DIR / "cleansed" / f"{job_id}_cleansed.csv"`
    - Create directories: `output_path.parent.mkdir(parents=True, exist_ok=True)`
    - Save DataFrame: `pd.DataFrame(dataset).to_csv(output_path, index=False)`
    - Return path

  - [ ] Implement `save_rejected_rows(job_id: str, rejected: List[Dict]) -> Path`
    - Same structure as `save_cleansed_dataset`
    - Handle empty list: write `"# No rejected rows\n"` if no rejections

  - [ ] Implement `save_profiling_snapshot(job_id: str, snapshot: ProfilingSnapshot) -> Path`
    - Path: `OUTPUTS_DIR / "profiling" / f"{job_id}_profile.json"`
    - Use Pydantic: `output_path.write_text(snapshot.json(indent=2))`

  - [ ] Implement `save_validation_result(job_id: str, result: Dict) -> Path`
    - Path: `OUTPUTS_DIR / "validation" / f"{job_id}_validation.json"`
    - Use `json.dump(result, f, indent=2)`

---

## Phase 4: Test Fixtures

- [ ] Create `tests/fixtures/tenant_fixtures.py`
  - [ ] Define `TENANT_ACME = {"tenant_id": "tenant-acme", "environment": "dev"}`
  - [ ] Define `TENANT_BETA = {"tenant_id": "tenant-beta", "environment": "test"}`
  - [ ] Define path constants:
    ```python
    FIXTURES_DIR = Path(__file__).parent
    DATASETS_DIR = FIXTURES_DIR / "datasets"
    OUTPUTS_DIR = FIXTURES_DIR / "outputs"
    ```
  - [ ] Implement `get_dataset_path(domain: str, filename: str) -> Path`

---

## Phase 5: End-to-End Integration Test

- [ ] Create `tests/integration/test_e2e_file_workflow.py`
  - [ ] Add path setup:
    ```python
    sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    ```

  - [ ] Implement `test_billing_valid_e2e_workflow()`
    - [ ] Load CSV with `load_csv_to_dict_list()`
    - [ ] Assert dataset has 3 rows
    - [ ] Define `CleansingRule` with transformations:
      - `standardize` on `Currency`
      - `fill_missing` on `CustomerId`
      - `deduplicate` on `InvoiceNumber`
    - [ ] Create `CleansingJob` with `TENANT_ACME["tenant_id"]`
    - [ ] Run `CleansingEngine.run(job, rule, dataset)`
    - [ ] Save cleansed dataset
    - [ ] Extract and save rejected rows
    - [ ] Create `ProfilingJob`
    - [ ] Run `ProfilingEngine.profile(profiling_job, cleansed_dataset)`
    - [ ] Save profiling snapshot
    - [ ] Assert:
      - `result.status == "succeeded"`
      - `result.after_counts["rows"] == 3`
      - `cleansed_dataset[0]["Currency"] == "USD"`
      - `profiling_result.snapshot.record_count == 3`
      - Files exist

  - [ ] Implement `test_billing_duplicates_workflow()`
    - [ ] Load `billing_duplicates.csv`
    - [ ] Define rule with only `deduplicate` transformation
    - [ ] Run cleansing
    - [ ] Save outputs
    - [ ] Assert:
      - `len(cleansed_dataset) < len(dataset)`
      - `result.after_counts["rejected"] > 0`

  - [ ] Implement `test_billing_missing_customer_workflow()`
    - [ ] Load `billing_missing_customer.csv`
    - [ ] Assert initial nulls: `dataset[1]["CustomerId"] is None`
    - [ ] Define rule with only `fill_missing` transformation
    - [ ] Run cleansing
    - [ ] Save outputs
    - [ ] Assert:
      - `cleansed_dataset[1]["CustomerId"] == "UNKNOWN"`
      - `result.status == "succeeded"`

---

## Phase 6: Run and Verify

### Run Tests

- [ ] Run all E2E tests:
  ```bash
  pytest tests/integration/test_e2e_file_workflow.py -v
  ```

- [ ] Run with output capture disabled (see print statements):
  ```bash
  pytest tests/integration/test_e2e_file_workflow.py -v -s
  ```

- [ ] All 3 tests pass:
  - [ ] `test_billing_valid_e2e_workflow`
  - [ ] `test_billing_duplicates_workflow`
  - [ ] `test_billing_missing_customer_workflow`

### Verify Outputs

- [ ] Inspect cleansed CSV:
  ```bash
  cat tests/fixtures/outputs/cleansed/e2e-billing-001_cleansed.csv
  ```
  - [ ] Currency values are uppercase (USD, EUR, GBP)

- [ ] Inspect profiling JSON:
  ```bash
  cat tests/fixtures/outputs/profiling/e2e-billing-001_profile.json | jq
  ```
  - [ ] Has `record_count: 3`
  - [ ] Has `field_stats` for `Amount`, `Currency`, etc.

- [ ] Inspect Amount field stats:
  ```bash
  cat tests/fixtures/outputs/profiling/e2e-billing-001_profile.json | jq '.field_stats.Amount'
  ```
  - [ ] Has `mean`, `stddev`, `min`, `max`

- [ ] List all generated outputs:
  ```bash
  find tests/fixtures/outputs -type f
  ```

---

## Phase 7: Documentation

- [ ] Create `tests/fixtures/README.md`
  - [ ] Document directory structure
  - [ ] List sample datasets with descriptions
  - [ ] Explain how to run tests
  - [ ] Explain how to inspect outputs
  - [ ] Document how to add new test files

---

## Verification Checklist

After completing all phases, verify:

### Functionality

- [ ] Can load CSV files into list-of-dicts format
- [ ] Can run cleansing on loaded data
- [ ] Can save cleansed datasets as CSV
- [ ] Can save rejected rows as CSV
- [ ] Can run profiling on cleansed data
- [ ] Can save profiling snapshots as JSON
- [ ] All 3 integration tests pass

### File Organization

- [ ] Input files in `tests/fixtures/datasets/{domain}/`
- [ ] Output files in `tests/fixtures/outputs/{type}/`
- [ ] Outputs are gitignored
- [ ] Directory structure is clean and logical

### Code Quality

- [ ] File loaders handle NaN correctly (replace with None)
- [ ] File savers create directories automatically
- [ ] File savers handle empty datasets gracefully
- [ ] Tests have clear assertions
- [ ] Tests use tenant fixtures consistently
- [ ] Code follows existing patterns (check critical files)

### Documentation

- [ ] README explains directory structure
- [ ] README documents sample datasets
- [ ] README shows how to run tests
- [ ] README shows how to inspect outputs

---

## Critical Files to Review

Before implementation, read these files:

- [ ] `src/dq_cleansing/engine/cleansing_engine.py` (lines 20-64)
  - Understand `run()` signature and return values

- [ ] `src/dq_profiling/engine/profiler.py` (lines 21-111)
  - Understand `profile()` signature and ProfilingSnapshot structure

- [ ] `rule_libraries/cleansing_rules/example_cleansing.rules.yaml`
  - Understand required field names and transformations

- [ ] `tests/integration/test_cleansing_routes.py` (lines 59-74)
  - Understand test patterns and assertions

- [ ] `src/dq_profiling/models/profiling_snapshot.py`
  - Understand ProfilingSnapshot model for JSON serialization

---

## Troubleshooting

If you encounter issues:

- [ ] **Import errors**: Run from repository root (`cd /path/to/data_quality_api`)
- [ ] **File not found**: Verify all CSV files created in Phase 1
- [ ] **Directory errors**: Manually create with `mkdir -p tests/fixtures/outputs/{...}`
- [ ] **Transformation errors**: Check `src/dq_cleansing/engine/transformer.py`
- [ ] **JSON serialization errors**: Use `snapshot.json()`, not `json.dumps(snapshot)`

---

## Success Criteria

You're done when:

✅ All 3 tests pass without errors
✅ Cleansed CSV shows uppercase currency codes
✅ Profiling JSON has field statistics with mean/stddev
✅ Can manually inspect all outputs
✅ README documents the workflow
✅ Outputs are gitignored

---

## Next Steps (After Completion)

After basic flow works, consider:

- [ ] Add validation engine integration (wire `dq_core.RuleEngine`)
- [ ] Add API upload endpoints (`POST /uploads` with multipart form)
- [ ] Add customer domain sample files
- [ ] Add transaction domain sample files
- [ ] Test Excel files with `load_excel_to_dict_list()`
- [ ] Add database persistence (implement Postgres stores)
- [ ] Add Azure Blob integration (for cloud storage)
- [ ] Add larger datasets for performance testing
- [ ] Add HTML report generation from profiling snapshots

---

## Time Estimates

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | Directories + CSV files + .gitignore | 15 minutes |
| Phase 2 | File loaders | 20 minutes |
| Phase 3 | File savers | 30 minutes |
| Phase 4 | Test fixtures | 15 minutes |
| Phase 5 | Integration tests | 60 minutes |
| Phase 6 | Run & verify | 20 minutes |
| Phase 7 | Documentation | 20 minutes |
| **Total** | | **~3 hours** |

---

## Notes

- Small CSV files (3-5 rows) are intentional - suitable for version control
- Tenant IDs are hardcoded for tests - no authentication needed
- Outputs are ephemeral - don't commit to git
- File loaders use pandas - already a dependency
- Engines work with `List[Dict]`, not DataFrames - no engine modifications needed
