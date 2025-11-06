import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_cleansing import CleansingRule, TransformationStep

from src.dq_api.routes import cleansing


def build_rule_payload() -> dict:
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
        ],
    )
    return rule.dict()


def create_client() -> TestClient:
    cleansing.reset_state()
    app = FastAPI()
    app.include_router(cleansing.router)
    return TestClient(app)


def test_cleansing_workflow_endpoints():
    client = create_client()

    # Upsert rule
    response = client.post("/cleansing/rules", json=build_rule_payload())
    assert response.status_code == 200
    assert response.json()["data"]["rule_id"] == "billing-standardise"

    # Run cleansing job
    payload = {
        "job_id": "cln-job-1",
        "tenant_id": "tenant-1",
        "dataset_type": "billing",
        "rule_id": "billing-standardise",
        "dataset": [
            {"InvoiceNumber": "INV-001", "Currency": "usd", "CustomerId": "C001"},
            {"InvoiceNumber": "INV-002", "Currency": "eur", "CustomerId": None},
        ],
    }
    run_response = client.post("/cleansing/jobs", json=payload)
    assert run_response.status_code == 200
    run_body = run_response.json()
    assert run_body["data"]["status"] == "succeeded"
    assert run_body["meta"]["cleansed_preview"][0]["Currency"] == "USD"

    # Retrieve job details
    job_response = client.get("/cleansing/jobs/cln-job-1")
    assert job_response.status_code == 200
    job_body = job_response.json()
    assert job_body["data"]["before_counts"]["rows"] == 2

    # Chain validation job
    chain_response = client.post("/cleansing/jobs/cln-job-1/chain-validation", json={})
    assert chain_response.status_code == 200
    assert chain_response.json()["data"]["linked_validation_job_id"].startswith("val-")

    # List jobs for completeness
    list_response = client.get("/cleansing/jobs")
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["count"] == 1
