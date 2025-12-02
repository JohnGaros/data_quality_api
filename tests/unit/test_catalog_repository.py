"""Unit tests for CatalogRepository attribute index functionality."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from dq_catalog.models import CatalogAttribute, CatalogEntity
from dq_catalog.repository import CatalogRepository
from dq_stores.memory import InMemoryStore


@pytest.fixture
def sample_entities() -> list[CatalogEntity]:
    """Create sample catalog entities for testing."""
    return [
        CatalogEntity(
            catalog_entity_id="customer_v1",
            name="Customer",
            description="Customer entity",
            domain="Sales",
            attributes=[
                CatalogAttribute(
                    catalog_attribute_id="customer_email_v1",
                    name="Email",
                    entity_id="customer_v1",
                    data_type="string",
                    description="Customer email address",
                    tags=["PII", "Contact"],
                ),
                CatalogAttribute(
                    catalog_attribute_id="customer_id_v1",
                    name="Customer ID",
                    entity_id="customer_v1",
                    data_type="string",
                    description="Unique customer identifier",
                    tags=["Primary Key"],
                ),
            ],
        ),
        CatalogEntity(
            catalog_entity_id="account_v1",
            name="Account",
            description="Account entity",
            domain="Finance",
            attributes=[
                CatalogAttribute(
                    catalog_attribute_id="account_number_v1",
                    name="Account Number",
                    entity_id="account_v1",
                    data_type="string",
                    description="Account identifier",
                ),
                CatalogAttribute(
                    catalog_attribute_id="account_balance_v1",
                    name="Balance",
                    entity_id="account_v1",
                    data_type="decimal",
                    description="Account balance",
                ),
            ],
        ),
    ]


@pytest.fixture
def catalog_repo(sample_entities) -> CatalogRepository:
    """Create a CatalogRepository with sample data."""
    store = InMemoryStore[str, CatalogEntity]()
    repo = CatalogRepository(store)

    # Add sample entities
    for entity in sample_entities:
        repo.put_entity(entity)

    return repo


def test_attribute_index_built_on_init(sample_entities) -> None:
    """Verify attribute index is built on repository initialization."""
    store = InMemoryStore[str, CatalogEntity]()

    # Populate store before creating repository
    for entity in sample_entities:
        store.put(entity.catalog_entity_id, entity)

    # Create repository - should build index
    repo = CatalogRepository(store)

    # Verify index contains all attributes
    assert len(repo._attribute_index) == 4
    assert repo._attribute_index["customer_email_v1"] == "customer_v1"
    assert repo._attribute_index["customer_id_v1"] == "customer_v1"
    assert repo._attribute_index["account_number_v1"] == "account_v1"
    assert repo._attribute_index["account_balance_v1"] == "account_v1"


def test_get_attribute_uses_index_for_o1_lookup(catalog_repo) -> None:
    """Verify get_attribute() uses index for O(1) lookup."""
    # Lookup attribute via index
    entity = catalog_repo.get_attribute("customer_email_v1")

    assert entity is not None
    assert entity.catalog_entity_id == "customer_v1"

    # Verify the attribute exists in the entity
    attr = next(
        (a for a in entity.attributes if a.catalog_attribute_id == "customer_email_v1"),
        None,
    )
    assert attr is not None
    assert attr.name == "Email"
    assert attr.data_type == "string"


def test_get_attribute_returns_none_for_nonexistent_id(catalog_repo) -> None:
    """Verify get_attribute() returns None for non-existent attribute."""
    entity = catalog_repo.get_attribute("nonexistent_attr_v1")
    assert entity is None


def test_put_entity_updates_index(catalog_repo) -> None:
    """Verify put_entity() updates the attribute index."""
    # Create new entity
    new_entity = CatalogEntity(
        catalog_entity_id="product_v1",
        name="Product",
        description="Product entity",
        domain="Inventory",
        attributes=[
            CatalogAttribute(
                catalog_attribute_id="product_sku_v1",
                name="SKU",
                entity_id="product_v1",
                data_type="string",
                description="Product SKU",
            ),
        ],
    )

    # Add to repository
    catalog_repo.put_entity(new_entity)

    # Verify index updated
    assert "product_sku_v1" in catalog_repo._attribute_index
    assert catalog_repo._attribute_index["product_sku_v1"] == "product_v1"

    # Verify lookup works
    entity = catalog_repo.get_attribute("product_sku_v1")
    assert entity is not None
    assert entity.catalog_entity_id == "product_v1"


def test_put_entity_overwrites_existing_index_entries(catalog_repo) -> None:
    """Verify put_entity() overwrites index when entity is updated."""
    # Get existing entity
    entity = catalog_repo.get_entity("customer_v1")
    assert entity is not None

    # Modify entity (add new attribute)
    modified_entity = entity.model_copy(deep=True)
    modified_entity.attributes.append(
        CatalogAttribute(
            catalog_attribute_id="customer_phone_v1",
            name="Phone",
            entity_id="customer_v1",
            data_type="string",
            description="Customer phone number",
            tags=["PII", "Contact"],
        )
    )

    # Update entity
    catalog_repo.put_entity(modified_entity)

    # Verify new attribute in index
    assert "customer_phone_v1" in catalog_repo._attribute_index
    assert catalog_repo._attribute_index["customer_phone_v1"] == "customer_v1"

    # Verify old attributes still in index
    assert "customer_email_v1" in catalog_repo._attribute_index
    assert "customer_id_v1" in catalog_repo._attribute_index

    # Verify lookup works for new attribute
    entity = catalog_repo.get_attribute("customer_phone_v1")
    assert entity is not None
    assert entity.catalog_entity_id == "customer_v1"


def test_attribute_index_consistency_after_multiple_operations(catalog_repo) -> None:
    """Verify index remains consistent after multiple add/update operations."""
    # Initial state: 4 attributes
    assert len(catalog_repo._attribute_index) == 4

    # Add new entity with 2 attributes
    entity1 = CatalogEntity(
        catalog_entity_id="order_v1",
        name="Order",
        attributes=[
            CatalogAttribute(
                catalog_attribute_id="order_id_v1",
                name="Order ID",
                entity_id="order_v1",
                data_type="string",
            ),
            CatalogAttribute(
                catalog_attribute_id="order_date_v1",
                name="Order Date",
                entity_id="order_v1",
                data_type="date",
            ),
        ],
    )
    catalog_repo.put_entity(entity1)
    assert len(catalog_repo._attribute_index) == 6

    # Update existing entity (add attribute)
    customer = catalog_repo.get_entity("customer_v1")
    customer.attributes.append(
        CatalogAttribute(
            catalog_attribute_id="customer_age_v1",
            name="Age",
            entity_id="customer_v1",
            data_type="integer",
        )
    )
    catalog_repo.put_entity(customer)
    assert len(catalog_repo._attribute_index) == 7

    # Verify all lookups work
    assert catalog_repo.get_attribute("order_id_v1") is not None
    assert catalog_repo.get_attribute("order_date_v1") is not None
    assert catalog_repo.get_attribute("customer_age_v1") is not None
    assert catalog_repo.get_attribute("customer_email_v1") is not None


def test_rebuild_index_clears_and_repopulates(catalog_repo) -> None:
    """Verify _rebuild_index() clears and repopulates the index."""
    # Initial state
    initial_count = len(catalog_repo._attribute_index)
    assert initial_count == 4

    # Manually corrupt the index
    catalog_repo._attribute_index["fake_attr_v1"] = "fake_entity_v1"
    assert len(catalog_repo._attribute_index) == 5

    # Rebuild index
    catalog_repo._rebuild_index()

    # Verify index restored to correct state
    assert len(catalog_repo._attribute_index) == initial_count
    assert "fake_attr_v1" not in catalog_repo._attribute_index
    assert "customer_email_v1" in catalog_repo._attribute_index


def test_list_entities_returns_all_entities(catalog_repo) -> None:
    """Verify list_entities() returns all entities."""
    entities = catalog_repo.list_entities()

    assert len(entities) == 2
    entity_ids = {e.catalog_entity_id for e in entities}
    assert entity_ids == {"customer_v1", "account_v1"}


def test_get_entity_returns_correct_entity(catalog_repo) -> None:
    """Verify get_entity() returns correct entity."""
    entity = catalog_repo.get_entity("customer_v1")

    assert entity is not None
    assert entity.catalog_entity_id == "customer_v1"
    assert entity.name == "Customer"
    assert len(entity.attributes) == 2


def test_get_entity_returns_none_for_nonexistent_id(catalog_repo) -> None:
    """Verify get_entity() returns None for non-existent entity."""
    entity = catalog_repo.get_entity("nonexistent_v1")
    assert entity is None


def test_attribute_lookup_performance_with_large_catalog() -> None:
    """Verify attribute lookup remains fast with large catalog (100 entities, 50 attrs each)."""
    store = InMemoryStore[str, CatalogEntity]()
    repo = CatalogRepository(store)

    # Create 100 entities with 50 attributes each (5000 total attributes)
    for i in range(100):
        entity_id = f"entity_{i}_v1"
        attributes = [
            CatalogAttribute(
                catalog_attribute_id=f"attr_{i}_{j}_v1",
                name=f"Attribute {j}",
                entity_id=entity_id,
                data_type="string",
            )
            for j in range(50)
        ]

        entity = CatalogEntity(
            catalog_entity_id=entity_id,
            name=f"Entity {i}",
            attributes=attributes,
        )
        repo.put_entity(entity)

    # Verify index size
    assert len(repo._attribute_index) == 5000

    # Verify lookup works for first and last attributes
    entity_first = repo.get_attribute("attr_0_0_v1")
    assert entity_first is not None
    assert entity_first.catalog_entity_id == "entity_0_v1"

    entity_last = repo.get_attribute("attr_99_49_v1")
    assert entity_last is not None
    assert entity_last.catalog_entity_id == "entity_99_v1"

    # Verify lookup works for mid-point attribute
    entity_mid = repo.get_attribute("attr_50_25_v1")
    assert entity_mid is not None
    assert entity_mid.catalog_entity_id == "entity_50_v1"


def test_deprecated_attribute_with_successor() -> None:
    """Verify deprecated attributes can reference their successor."""
    from datetime import datetime

    store = InMemoryStore[str, CatalogEntity]()
    repo = CatalogRepository(store)

    # Create entity with deprecated attribute pointing to successor
    entity = CatalogEntity(
        catalog_entity_id="customer_v1",
        name="Customer",
        attributes=[
            CatalogAttribute(
                catalog_attribute_id="customer_email_v1",
                name="Email (Legacy)",
                entity_id="customer_v1",
                data_type="string",
                deprecated=True,
                successor_id="customer_email_v2",
                deprecation_date=datetime(2025, 1, 15),
            ),
            CatalogAttribute(
                catalog_attribute_id="customer_email_v2",
                name="Email",
                entity_id="customer_v1",
                data_type="string",
                description="Customer email with improved validation",
            ),
        ],
    )
    repo.put_entity(entity)

    # Verify deprecated attribute has successor info
    parent = repo.get_attribute("customer_email_v1")
    assert parent is not None
    deprecated_attr = next(
        a for a in parent.attributes if a.catalog_attribute_id == "customer_email_v1"
    )
    assert deprecated_attr.deprecated is True
    assert deprecated_attr.successor_id == "customer_email_v2"
    assert deprecated_attr.deprecation_date == datetime(2025, 1, 15)

    # Verify successor attribute exists and is not deprecated
    successor_attr = next(
        a for a in parent.attributes if a.catalog_attribute_id == "customer_email_v2"
    )
    assert successor_attr.deprecated is False
    assert successor_attr.successor_id is None


def test_deprecated_entity_with_successor() -> None:
    """Verify deprecated entities can reference their successor."""
    from datetime import datetime

    store = InMemoryStore[str, CatalogEntity]()
    repo = CatalogRepository(store)

    # Create deprecated entity
    old_entity = CatalogEntity(
        catalog_entity_id="customer_v1",
        name="Customer (Legacy)",
        deprecated=True,
        successor_id="customer_v2",
        deprecation_date=datetime(2025, 1, 15),
        attributes=[
            CatalogAttribute(
                catalog_attribute_id="customer_id_v1",
                name="ID",
                entity_id="customer_v1",
                data_type="string",
            ),
        ],
    )

    # Create successor entity
    new_entity = CatalogEntity(
        catalog_entity_id="customer_v2",
        name="Customer",
        description="Improved customer entity with additional fields",
        attributes=[
            CatalogAttribute(
                catalog_attribute_id="customer_id_v2",
                name="ID",
                entity_id="customer_v2",
                data_type="uuid",
            ),
        ],
    )

    repo.put_entity(old_entity)
    repo.put_entity(new_entity)

    # Verify deprecated entity has successor info
    retrieved_old = repo.get_entity("customer_v1")
    assert retrieved_old is not None
    assert retrieved_old.deprecated is True
    assert retrieved_old.successor_id == "customer_v2"
    assert retrieved_old.deprecation_date == datetime(2025, 1, 15)

    # Verify successor entity exists and is not deprecated
    retrieved_new = repo.get_entity("customer_v2")
    assert retrieved_new is not None
    assert retrieved_new.deprecated is False
    assert retrieved_new.successor_id is None
