"""Compliance helpers for metadata governance."""

from datetime import datetime, timedelta
from typing import Optional

from .models import ComplianceTag, ValidationJobMetadata


class RetentionPolicy:
    """Represents a simple retention policy in days."""

    def __init__(self, policy_id: str, days: int) -> None:
        self.policy_id = policy_id
        self.days = days

    def expires_at(self, reference: datetime) -> datetime:
        """Return the timestamp when artifacts expire."""
        return reference + timedelta(days=self.days)


def requires_privileged_access(tag: ComplianceTag) -> bool:
    """Check if a compliance tag requires elevated permissions."""
    sensitive_keys = {"PII", "PCI", "PHI"}
    return tag.tag_key.upper() in sensitive_keys


def is_job_within_retention(job: ValidationJobMetadata, retention_policy: RetentionPolicy) -> bool:
    """Validate whether a job's artifacts are still within retention window."""
    reference = job.completed_at or job.submitted_at
    expiry = retention_policy.expires_at(reference)
    return datetime.utcnow() <= expiry


def enforce_tag_removal(tag: ComplianceTag, justification: Optional[str]) -> None:
    """Ensure tag removals capture justification for auditability."""
    if requires_privileged_access(tag) and not justification:
        raise ValueError("Removing sensitive classification requires justification.")
