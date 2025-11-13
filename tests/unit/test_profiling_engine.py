import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_profiling.engine.profiler import ProfilingEngine
from dq_profiling.models.profiling_job import ProfilingJob
from dq_profiling.report.profiling_report import profiling_report_from_result


def build_job() -> ProfilingJob:
    return ProfilingJob(
        job_id="profile-job-1",
        tenant_id="tenant-1",
        dataset_type="billing",
    )


def sample_dataset():
    return [
        {"Amount": 10, "Status": "PAID"},
        {"Amount": 20, "Status": "FAILED"},
        {"Amount": None, "Status": "PAID"},
        {"Amount": 30, "Status": "PAID"},
    ]


def test_profiling_engine_computes_numeric_and_categorical_stats():
    engine = ProfilingEngine(sample_size=2)

    result = engine.profile(build_job(), sample_dataset())

    amount_stats = result.snapshot.field_stats["Amount"]
    status_stats = result.snapshot.field_stats["Status"]

    assert amount_stats.non_null == 3
    assert amount_stats.nulls == 1
    assert amount_stats.min_value == 10.0
    assert amount_stats.max_value == 30.0
    assert amount_stats.mean == pytest.approx(20.0)
    assert amount_stats.stddev == pytest.approx(8.1649, rel=1e-3)
    assert amount_stats.distribution is not None
    assert amount_stats.distribution.kind == "numeric"
    assert sum(bucket.count for bucket in amount_stats.distribution.buckets) == 3

    assert status_stats.frequent_values[0].value == "PAID"
    assert status_stats.frequent_values[0].count == 3
    assert status_stats.frequent_values[0].percentage == pytest.approx(75.0)
    assert status_stats.distribution is not None
    assert status_stats.distribution.kind == "categorical"
    assert len(status_stats.distribution.values) == 2


def test_profiling_report_surfaces_extended_metrics():
    engine = ProfilingEngine(sample_size=2)
    result = engine.profile(build_job(), sample_dataset())

    report = profiling_report_from_result(result)
    amount_summary = next(field for field in report.field_summaries if field.name == "Amount")

    assert amount_summary.mean == pytest.approx(20.0)
    assert "frequent_values" in amount_summary.to_dict()
    rows = list(report.to_rows())
    assert rows[0][:4] == ["field_name", "non_null", "nulls", "distinct"]
