"""Semantic data catalog models (entities, attributes, relationships)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CatalogAttribute(BaseModel):
    """Canonical attribute definition (semantic, not physical)."""

    catalog_attribute_id: str = Field(..., description="Unique identifier for the attribute.")
    name: str = Field(..., description="Human-friendly attribute name (e.g., email).")
    entity_id: str = Field(..., description="Owning catalog entity ID.")
    data_type: str = Field(..., description="Semantic data type (string, decimal, date, etc.).")
    description: Optional[str] = Field(None, description="Business meaning of the attribute.")
    tags: List[str] = Field(default_factory=list, description="Labels/domains (e.g., PII, Retail).")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom attribute metadata.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CatalogEntity(BaseModel):
    """Canonical entity within the data catalog."""

    catalog_entity_id: str = Field(..., description="Unique entity identifier (e.g., customer).")
    name: str = Field(..., description="Display name for the entity.")
    description: Optional[str] = Field(None, description="Business definition of the entity.")
    domain: Optional[str] = Field(None, description="Domain/subject area (e.g., Retail, Finance).")
    attributes: List[CatalogAttribute] = Field(default_factory=list, description="Attributes belonging to this entity.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom entity metadata.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CatalogRelationship(BaseModel):
    """Relationship between catalog entities."""

    relationship_id: str = Field(..., description="Unique relationship identifier.")
    from_entity_id: str = Field(..., description="Source entity ID.")
    to_entity_id: str = Field(..., description="Target entity ID.")
    relationship_type: str = Field(..., description="Type (owns, references, feeds, etc.).")
    description: Optional[str] = Field(None, description="Notes on the relationship semantics.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom relationship metadata.")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
