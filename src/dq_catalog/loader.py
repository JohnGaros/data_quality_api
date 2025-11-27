"""Loader for YAML catalog definitions.

Parses YAML files from `catalog_libraries/` and converts them into
CatalogEntity and CatalogAttribute models.
"""

import os
import yaml
from typing import List, Dict, Any
from pathlib import Path

from dq_catalog.models import CatalogEntity, CatalogAttribute


class CatalogLoader:
    """Loads catalog entities from YAML files."""

    def load_from_yaml(self, file_path: str) -> List[CatalogEntity]:
        """Load catalog entities from a single YAML file.

        Args:
            file_path: Path to the YAML file.

        Returns:
            List of CatalogEntity objects parsed from the file.
        """
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        if not data or "entities" not in data:
            return []

        entities = []
        for entity_data in data["entities"]:
            # Ensure attributes are parsed as CatalogAttribute models
            if "attributes" in entity_data:
                # Inject parent entity_id if missing
                parent_id = entity_data.get("catalog_entity_id")
                for attr in entity_data["attributes"]:
                    if "entity_id" not in attr and parent_id:
                        attr["entity_id"] = parent_id
                
                entity_data["attributes"] = [
                    CatalogAttribute(**attr) for attr in entity_data["attributes"]
                ]
            
            # Create Entity
            entity = CatalogEntity(**entity_data)
            entities.append(entity)

        return entities

    def load_directory(self, directory_path: str) -> List[CatalogEntity]:
        """Recursively load all YAML files in a directory.

        Args:
            directory_path: Root directory to search.

        Returns:
            Aggregated list of all CatalogEntity objects found.
        """
        all_entities = []
        root = Path(directory_path)

        if not root.exists():
            return []

        for file_path in root.rglob("*.yaml"):
            try:
                entities = self.load_from_yaml(str(file_path))
                all_entities.extend(entities)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                # In a real app, we might want to raise or collect errors
                continue
        
        return all_entities
