from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from .cleansing_rule import CleansingRule


class CleansingRuleLibrary:
    """In-memory registry for cleansing rules.

    A production implementation would persist to a database or config store,
    but the library abstraction keeps orchestration decoupled from storage.
    """

    def __init__(self) -> None:
        self._rules: Dict[Tuple[str, str], CleansingRule] = {}

    def upsert(self, rule: CleansingRule) -> None:
        """Store or replace a rule version."""
        self._rules[(rule.rule_id, rule.version)] = rule

    def get(
        self,
        rule_id: str,
        version: Optional[str] = None,
    ) -> Optional[CleansingRule]:
        """Fetch a rule by id and optional version."""
        if version:
            return self._rules.get((rule_id, version))

        # Return the newest version lexicographically if unspecified.
        matching: List[Tuple[str, str]] = [
            key for key in self._rules if key[0] == rule_id
        ]
        if not matching:
            return None
        latest_key = sorted(matching, key=lambda item: item[1])[-1]
        return self._rules[latest_key]

    def list(self, dataset_type: Optional[str] = None) -> Iterable[CleansingRule]:
        """Return all rules, optionally filtered by dataset."""
        for rule in self._rules.values():
            if dataset_type and rule.dataset_type != dataset_type:
                continue
            yield rule

    def clear(self) -> None:
        """Utility for tests to reset registry state."""
        self._rules.clear()
