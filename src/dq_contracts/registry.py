"""Minimal registry stub showing canonical JSON ready for Postgres JSONB persistence."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping, Optional

from .models import DataContract, RuleBinding, RuleTemplate
from .serialization import to_canonical_json


class ContractRegistry:
    """
    Registry facade that prepares contract and rule records for storage.

    This stub demonstrates how canonical JSON produced by Pydantic models
    should be stored in JSONB columns. Provide a `db_writer` callable to
    persist records using your database layer (e.g., SQLAlchemy, psycopg).
    """

    def __init__(self, db_writer: Optional[Callable] = None) -> None:
        self._db_writer = db_writer

    def prepare_contract_record(self, contract: DataContract) -> dict[str, Any]:
        """Normalise a DataContract into a JSONB-ready record."""

        payload = to_canonical_json(contract)
        return {
            "contract_id": contract.contract_id,
            "tenant_id": contract.tenant_id,
            "environment": contract.environment.value,
            "version": contract.version,
            "payload": payload,  # Stored in a JSONB column
        }

    def prepare_rule_template_records(self, templates: Iterable[RuleTemplate]) -> list[dict[str, Any]]:
        """Normalise rule templates into JSONB-ready records."""

        records = []
        for template in templates:
            payload = to_canonical_json(template)
            records.append(
                {
                    "rule_template_id": template.rule_template_id,
                    "tenant_id": getattr(template, "tenant_id", None),  # Optional tenant scoping
                    "rule_type": template.rule_type.value,
                    "version": template.version,
                    "payload": payload,
                }
            )
        return records

    def prepare_rule_binding_records(self, bindings: Iterable[RuleBinding]) -> list[dict[str, Any]]:
        """Normalise rule bindings into JSONB-ready records."""

        records = []
        for binding in bindings:
            payload = to_canonical_json(binding)
            records.append(
                {
                    "binding_id": binding.binding_id,
                    "tenant_id": binding.tenant_id,
                    "environment": binding.environment.value,
                    "rule_template_id": binding.rule_template_id,
                    "payload": payload,
                }
            )
        return records

    def persist(self, table: str, records: Iterable[Mapping[str, Any]]) -> None:
        """
        Persist prepared records using the provided db_writer.

        In production, `db_writer` should insert into a JSONB-backed table. This stub
        raises when no writer is provided to avoid accidental no-op.
        """

        if not self._db_writer:
            raise NotImplementedError("No db_writer configured for ContractRegistry stub")
        self._db_writer(table=table, records=list(records))


__all__ = ["ContractRegistry"]
