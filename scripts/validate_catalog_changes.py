#!/usr/bin/env python3
"""Validate catalog YAML changes to enforce append-only versioning.

This script compares catalog YAML changes against Git HEAD to ensure:
1. Existing entity/attribute IDs are not modified in-place
2. Breaking changes require new versioned IDs (e.g., attr_v1 → attr_v2)
3. Non-breaking enrichment (tags, metadata) is allowed

Usage:
    python scripts/validate_catalog_changes.py

Exit codes:
    0 - All changes valid
    1 - Validation failed (breaking changes detected)
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class CatalogValidationError(Exception):
    """Raised when catalog changes violate append-only versioning rules."""

    pass


def get_git_head_content(file_path: str) -> Dict[str, Any]:
    """Load YAML content from Git HEAD.

    Args:
        file_path: Path to YAML file relative to repo root

    Returns:
        Parsed YAML content from HEAD, or empty dict if file is new
    """
    result = subprocess.run(
        ["git", "show", f"HEAD:{file_path}"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        # File doesn't exist in HEAD (new file)
        return {}

    try:
        content = yaml.safe_load(result.stdout)
        return content if content else {}
    except yaml.YAMLError as e:
        print(f"Warning: Failed to parse YAML from HEAD for {file_path}: {e}")
        return {}


def get_changed_catalog_files() -> List[str]:
    """Get list of changed catalog YAML files in staging area.

    Returns:
        List of file paths relative to repo root
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        capture_output=True,
        text=True,
        check=True,
    )

    changed_files = result.stdout.strip().split("\n")

    # Filter for catalog library YAML files
    catalog_files = [
        f
        for f in changed_files
        if f.startswith("catalog_libraries/") and f.endswith(".yaml")
    ]

    return catalog_files


def validate_no_entity_breaking_changes(
    old_entity: Dict[str, Any], new_entity: Dict[str, Any]
) -> None:
    """Validate that entity-level changes are non-breaking.

    Args:
        old_entity: Entity definition from HEAD
        new_entity: Entity definition from working tree

    Raises:
        CatalogValidationError: If breaking changes detected
    """
    entity_id = old_entity.get("catalog_entity_id")

    # Check: entity name changed without deprecation
    if old_entity.get("name") != new_entity.get("name"):
        if not new_entity.get("deprecated", False):
            raise CatalogValidationError(
                f"Entity {entity_id}: 'name' changed from '{old_entity.get('name')}' "
                f"to '{new_entity.get('name')}' without deprecation flag. "
                f"Create new entity ID (e.g., {entity_id}_v2) instead."
            )

    # Check: domain changed (semantic change)
    if old_entity.get("domain") != new_entity.get("domain"):
        if not new_entity.get("deprecated", False):
            raise CatalogValidationError(
                f"Entity {entity_id}: 'domain' changed without deprecation. "
                f"Domain changes are semantic. Create new entity ID instead."
            )

    # Check: newly deprecated entity should have successor_id
    if new_entity.get("deprecated", False) and not old_entity.get("deprecated", False):
        if not new_entity.get("successor_id"):
            print(
                f"  ⚠ Warning: Entity {entity_id} deprecated without successor_id. "
                f"Consider adding successor_id to help consumers migrate."
            )


def validate_no_attribute_breaking_changes(
    old_attr: Dict[str, Any], new_attr: Dict[str, Any]
) -> None:
    """Validate that attribute-level changes are non-breaking.

    Breaking changes require creating a new attribute ID.
    Non-breaking enrichment (tags, metadata, description) is allowed.

    Args:
        old_attr: Attribute definition from HEAD
        new_attr: Attribute definition from working tree

    Raises:
        CatalogValidationError: If breaking changes detected
    """
    attr_id = old_attr.get("catalog_attribute_id")

    # Breaking field changes
    breaking_fields = {
        "data_type": "Data type changes are breaking (affects validation rules)",
        "name": "Name changes affect semantic meaning",
        "entity_id": "Entity ID cannot be changed",
    }

    for field, reason in breaking_fields.items():
        old_value = old_attr.get(field)
        new_value = new_attr.get(field)

        if old_value != new_value:
            raise CatalogValidationError(
                f"Attribute {attr_id}: Breaking change to '{field}'. "
                f"{reason}. "
                f"Create new attribute ID (e.g., {attr_id}_v2) instead. "
                f"Old: {old_value}, New: {new_value}"
            )

    # Check: newly deprecated attribute should have successor_id
    if new_attr.get("deprecated", False) and not old_attr.get("deprecated", False):
        if not new_attr.get("successor_id"):
            print(
                f"  ⚠ Warning: Attribute {attr_id} deprecated without successor_id. "
                f"Consider adding successor_id to help consumers migrate."
            )

    # Non-breaking changes allowed (informational only)
    non_breaking_fields = ["tags", "format", "description", "metadata", "successor_id", "deprecation_date"]
    changed_fields = []

    for field in non_breaking_fields:
        if old_attr.get(field) != new_attr.get(field):
            changed_fields.append(field)

    if changed_fields:
        print(
            f"  → Non-breaking enrichment for {attr_id}: {', '.join(changed_fields)}"
        )


def validate_entity_changes(
    old_entities_map: Dict[str, Dict[str, Any]],
    new_entities_map: Dict[str, Dict[str, Any]],
) -> None:
    """Validate changes to entities and their attributes.

    Args:
        old_entities_map: Entity ID → entity dict from HEAD
        new_entities_map: Entity ID → entity dict from working tree

    Raises:
        CatalogValidationError: If breaking changes detected
    """
    # Check for modified entities
    for entity_id, old_entity in old_entities_map.items():
        if entity_id in new_entities_map:
            new_entity = new_entities_map[entity_id]

            # Validate entity-level changes
            validate_no_entity_breaking_changes(old_entity, new_entity)

            # Validate attribute-level changes
            old_attrs = {
                a["catalog_attribute_id"]: a
                for a in old_entity.get("attributes", [])
            }
            new_attrs = {
                a["catalog_attribute_id"]: a
                for a in new_entity.get("attributes", [])
            }

            for attr_id, old_attr in old_attrs.items():
                if attr_id in new_attrs:
                    # Attribute exists in both → validate no breaking changes
                    validate_no_attribute_breaking_changes(old_attr, new_attrs[attr_id])

    # Check for removed entities (without deprecation)
    for entity_id, old_entity in old_entities_map.items():
        if entity_id not in new_entities_map:
            raise CatalogValidationError(
                f"Entity {entity_id} removed without marking as deprecated. "
                f"Set 'deprecated: true' instead of deleting."
            )


def validate_catalog_yaml_file(file_path: str) -> None:
    """Validate a single catalog YAML file.

    Args:
        file_path: Path to YAML file relative to repo root

    Raises:
        CatalogValidationError: If validation fails
    """
    print(f"Validating {file_path}...")

    # Load old content from Git HEAD
    old_content = get_git_head_content(file_path)

    # Load new content from working tree
    with open(file_path, "r") as f:
        new_content = yaml.safe_load(f)

    if not old_content:
        print(f"  → New file, skipping validation")
        return

    if not new_content or "entities" not in new_content:
        raise CatalogValidationError(
            f"{file_path}: Invalid YAML structure (missing 'entities' key)"
        )

    # Build entity maps
    old_entities_map = {
        e["catalog_entity_id"]: e for e in old_content.get("entities", [])
    }
    new_entities_map = {
        e["catalog_entity_id"]: e for e in new_content.get("entities", [])
    }

    # Validate changes
    validate_entity_changes(old_entities_map, new_entities_map)

    print(f"  ✓ Validation passed")


def validate_all_catalog_changes() -> None:
    """Validate all changed catalog YAML files.

    Raises:
        CatalogValidationError: If any file fails validation
    """
    changed_files = get_changed_catalog_files()

    if not changed_files:
        print("No catalog changes detected")
        return

    print(f"Found {len(changed_files)} changed catalog file(s)\n")

    for file_path in changed_files:
        validate_catalog_yaml_file(file_path)

    print(f"\n✓ All catalog changes are valid")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 = success, 1 = validation failed)
    """
    try:
        validate_all_catalog_changes()
        return 0
    except CatalogValidationError as e:
        print(f"\n✗ Validation failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
