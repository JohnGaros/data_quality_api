"""Data Contracts API endpoints.

Handles creation and retrieval of Data Contracts, enforcing validation against
the Global Data Catalog.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from dq_catalog.repository import CatalogRepository
from dq_contracts.models import DataContract
from dq_api.dependencies import get_catalog_repository

# Note: In a real app, we'd need a ContractRepository/Store too.
# For this refactor, we focus on the validation logic.

router = APIRouter(prefix="/contracts", tags=["Data Contracts"])


def validate_contract_against_catalog(
    contract: DataContract, catalog_repo: CatalogRepository
) -> None:
    """Validate that contract references exist in the global catalog."""
    for dataset in contract.datasets:
        entity_ids = dataset.catalog_entity_ids or []

        # Validate Entity IDs
        for entity_id in entity_ids:
            entity = catalog_repo.get_entity(entity_id)
            if not entity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Referenced catalog entity '{entity_id}' not found.",
                )

        # Validate Attribute IDs
        for col in dataset.columns:
            if col.catalog_attribute_id:
                # In a real implementation, we'd check if the attribute exists
                # AND if it belongs to the correct entity (if entity is specified).
                # For MVP, we just check existence if we can resolve it.
                # Since our repo currently scans, this is expensive but correct.
                parent_entity = catalog_repo.get_attribute(col.catalog_attribute_id)
                if not parent_entity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Referenced catalog attribute '{col.catalog_attribute_id}' not found.",
                    )
                
                # Optional: Check if attribute belongs to the dataset's entity
                if entity_ids and parent_entity.catalog_entity_id not in set(entity_ids):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Attribute '{col.catalog_attribute_id}' belongs to entity "
                            f"'{parent_entity.catalog_entity_id}', but dataset maps to "
                            f"{entity_ids}."
                        ),
                    )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_contract(
    contract: DataContract,
    catalog_repo: CatalogRepository = Depends(get_catalog_repository),
) -> DataContract:
    """Create a new Data Contract.
    
    Validates that referenced catalog entities and attributes exist in the Global Catalog.
    """
    validate_contract_against_catalog(contract, catalog_repo)
    
    # TODO: Persist contract using ContractStore
    # For now, just return it to prove validation passed
    return contract
