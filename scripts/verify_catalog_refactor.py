"""Verification script for Global Catalog Refactor.

Tests:
1. Global Catalog Entity/Attribute creation (Append-Only).
2. Contract validation against Global Catalog.
3. Error handling for invalid references.
"""

import sys
from datetime import datetime

# Add src to path
sys.path.append("src")

from dq_catalog.models import CatalogEntity, CatalogAttribute
from dq_catalog.repository import CatalogRepository
from dq_contracts.models import DataContract, DatasetContract, ColumnContract, Environment, ContractStatus
from dq_stores.memory import InMemoryStore
from dq_api.routes.contracts import validate_contract_against_catalog
from fastapi import HTTPException

def run_verification():
    print("--- Starting Verification ---")

    # 1. Setup Global Catalog
    print("\n[1] Setting up Global Catalog...")
    store = InMemoryStore[str, CatalogEntity]()
    repo = CatalogRepository(store)

    # Create Entity: Customer (v1)
    customer_entity = CatalogEntity(
        catalog_entity_id="customer_v1",
        name="Customer",
        description="Global Customer Entity",
        attributes=[
            CatalogAttribute(
                catalog_attribute_id="customer_email_v1",
                name="Email",
                entity_id="customer_v1",
                data_type="string",
                description="Personal Email"
            )
        ]
    )
    repo.put_entity(customer_entity)
    print("    Created entity: customer_v1")

    # 2. Create Valid Contract
    print("\n[2] Testing Valid Contract...")
    contract = DataContract(
        contract_id="contract_1",
        tenant_id="tenant_a",
        environment=Environment.DEV,
        version="1.0.0",
        name="Customer Feed",
        datasets=[
            DatasetContract(
                dataset_contract_id="ds_1",
                dataset_type="customer_master",
                tenant_id="tenant_a",
                environment=Environment.DEV,
                version="1.0.0",
                catalog_entity_ids=["customer_v1"], # Valid Reference
                columns=[
                    ColumnContract(
                        column_id="col_email",
                        data_type="string",
                        catalog_attribute_id="customer_email_v1" # Valid Reference
                    )
                ]
            )
        ]
    )

    try:
        validate_contract_against_catalog(contract, repo)
        print("    SUCCESS: Valid contract passed validation.")
    except Exception as e:
        print(f"    FAILURE: Valid contract failed validation: {e}")
        sys.exit(1)

    # 3. Test Invalid Entity Reference
    print("\n[3] Testing Invalid Entity Reference...")
    invalid_entity_contract = contract.model_copy(deep=True)
    invalid_entity_contract.datasets[0].catalog_entity_ids = ["non_existent_entity"]
    
    try:
        validate_contract_against_catalog(invalid_entity_contract, repo)
        print("    FAILURE: Invalid entity contract passed validation (should fail).")
        sys.exit(1)
    except HTTPException as e:
        print(f"    SUCCESS: Caught expected error: {e.detail}")

    # 4. Test Invalid Attribute Reference
    print("\n[4] Testing Invalid Attribute Reference...")
    invalid_attr_contract = contract.model_copy(deep=True)
    invalid_attr_contract.datasets[0].columns[0].catalog_attribute_id = "non_existent_attr"

    try:
        validate_contract_against_catalog(invalid_attr_contract, repo)
        print("    FAILURE: Invalid attribute contract passed validation (should fail).")
        sys.exit(1)
    except HTTPException as e:
        print(f"    SUCCESS: Caught expected error: {e.detail}")

    # 5. Test Mismatched Attribute/Entity
    print("\n[5] Testing Mismatched Attribute/Entity...")
    # Create another entity to cause mismatch
    product_entity = CatalogEntity(
        catalog_entity_id="product_v1",
        name="Product",
        attributes=[
             CatalogAttribute(
                catalog_attribute_id="product_sku_v1",
                name="SKU",
                entity_id="product_v1",
                data_type="string"
            )
        ]
    )
    repo.put_entity(product_entity)

    mismatch_contract = contract.model_copy(deep=True)
    # Dataset maps to Customer, but column maps to Product SKU
    mismatch_contract.datasets[0].catalog_entity_ids = ["customer_v1"]
    mismatch_contract.datasets[0].columns[0].catalog_attribute_id = "product_sku_v1"

    try:
        validate_contract_against_catalog(mismatch_contract, repo)
        print("    FAILURE: Mismatched contract passed validation (should fail).")
        sys.exit(1)
    except HTTPException as e:
        print(f"    SUCCESS: Caught expected error: {e.detail}")

    print("\n--- Verification Complete: ALL TESTS PASSED ---")

if __name__ == "__main__":
    run_verification()
