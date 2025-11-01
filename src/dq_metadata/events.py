"""Common metadata events emitted across the platform."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


@dataclass(frozen=True)
class MetadataEvent:
    """Base event type with shared fields."""

    event_type: str
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    actor: Optional[str] = None
    tenant_id: Optional[str] = None
    payload: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationJobEvent(MetadataEvent):
    """Event describing validation job lifecycle milestones."""

    job_id: str = ""
    status: str = ""


@dataclass(frozen=True)
class RuleVersionEvent(MetadataEvent):
    """Event emitted when rule metadata changes."""

    rule_id: str = ""
    rule_version_id: str = ""
    change_type: str = ""
