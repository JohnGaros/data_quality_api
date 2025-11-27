"""Seed the Global Catalog from YAML definitions.

Reads all YAML files in `catalog_libraries/` and persists them to the
configured Catalog Repository.
"""

import sys
import os

# Add src to path
sys.path.append("src")

from dq_catalog.loader import CatalogLoader
from dq_api.dependencies import get_catalog_repository

def seed_catalog():
    print("--- Seeding Global Catalog ---")
    
    loader = CatalogLoader()
    repo = get_catalog_repository()
    
    catalog_dir = "catalog_libraries"
    if not os.path.exists(catalog_dir):
        print(f"Warning: Directory '{catalog_dir}' not found. Skipping seed.")
        return

    print(f"Loading entities from '{catalog_dir}'...")
    entities = loader.load_directory(catalog_dir)
    
    if not entities:
        print("No entities found.")
        return

    print(f"Found {len(entities)} entities. Persisting...")
    for entity in entities:
        repo.put_entity(entity)
        print(f"  - Persisted: {entity.catalog_entity_id} ({entity.name})")

    print("--- Seeding Complete ---")

if __name__ == "__main__":
    seed_catalog()
