from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from dq_cleansing import CleansingJob, CleansingRule

from ..services.cleansing_job_manager import CleansingJobManager

router = APIRouter(prefix="/cleansing", tags=["cleansing"])

_manager = CleansingJobManager()


def get_cleansing_manager() -> CleansingJobManager:
    return _manager


class CleansingJobPayload(BaseModel):
    job_id: str
    tenant_id: str
    dataset_type: str
    rule_id: str
    rule_version: Optional[str] = None
    chain_validation: bool = False
    dataset: List[Dict[str, Any]] = Field(default_factory=list)
    options: Dict[str, Any] = Field(default_factory=dict)


class ChainValidationPayload(BaseModel):
    validation_job_id: Optional[str] = None


@router.get("/rules")
def list_rules(
    manager: CleansingJobManager = Depends(get_cleansing_manager),
) -> Dict[str, Any]:
    rules = [rule.describe() for rule in manager.list_rules()]
    return {"data": rules, "meta": {"count": len(rules)}, "errors": []}


@router.post("/rules")
def upsert_rule(
    rule: CleansingRule,
    manager: CleansingJobManager = Depends(get_cleansing_manager),
) -> Dict[str, Any]:
    manager.upsert_rule(rule)
    return {"data": rule.describe(), "meta": {}, "errors": []}


@router.get("/jobs")
def list_jobs(
    manager: CleansingJobManager = Depends(get_cleansing_manager),
) -> Dict[str, Any]:
    results = [result.to_report_dict() for result in manager.list_job_results()]
    return {"data": results, "meta": {"count": len(results)}, "errors": []}


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    manager: CleansingJobManager = Depends(get_cleansing_manager),
) -> Dict[str, Any]:
    result = manager.get_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cleansing job not found")
    return {"data": result.to_report_dict(), "meta": {}, "errors": []}


@router.post("/jobs")
def run_job(
    payload: CleansingJobPayload,
    manager: CleansingJobManager = Depends(get_cleansing_manager),
) -> Dict[str, Any]:
    job = CleansingJob(
        job_id=payload.job_id,
        tenant_id=payload.tenant_id,
        dataset_type=payload.dataset_type,
        rule_id=payload.rule_id,
        rule_version=payload.rule_version,
        chain_validation=payload.chain_validation,
        options=payload.options,
    )
    result, cleansed_dataset, warnings = manager.submit_job(job, payload.dataset)
    meta = {
        "warnings": warnings,
        "cleansed_preview": cleansed_dataset[:3],
    }
    return {"data": result.to_report_dict(), "meta": meta, "errors": []}


@router.post("/jobs/{job_id}/chain-validation")
def chain_validation(
    job_id: str,
    payload: ChainValidationPayload,
    manager: CleansingJobManager = Depends(get_cleansing_manager),
) -> Dict[str, Any]:
    validation_job_id = payload.validation_job_id or f"val-{uuid4().hex[:8]}"
    updated = manager.link_validation_job(job_id, validation_job_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Cleansing job not found")
    return {
        "data": {
            "job_id": job_id,
            "linked_validation_job_id": validation_job_id,
        },
        "meta": {},
        "errors": [],
    }


def reset_state() -> None:
    """Reset in-memory caches (primarily for tests)."""
    _manager.reset()
