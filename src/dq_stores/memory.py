"""In-memory store implementation for testing and local development."""

from typing import Dict, Generic, Iterable, Optional, TypeVar

from dq_stores.base import Store

T = TypeVar("T")
Key = TypeVar("Key")


class InMemoryStore(Store[Key, T], Generic[Key, T]):
    """Simple in-memory store using a dictionary."""

    def __init__(self) -> None:
        self._data: Dict[Key, T] = {}

    def get(self, key: Key) -> Optional[T]:
        return self._data.get(key)

    def put(self, key: Key, value: T) -> None:
        self._data[key] = value

    def list(self, **filters) -> Iterable[T]:
        # Basic list without filtering for now
        return self._data.values()

    def delete(self, key: Key) -> None:
        if key in self._data:
            del self._data[key]
