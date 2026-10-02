"""Data access for todos.

TodoRepository is the contract the service depends on. MongoTodoRepository
is the real implementation; tests use a lightweight in-memory one. Swapping
storage (another database, a cache in front) means writing a new class here,
without touching the service or the views.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from pymongo import DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from todos.entities import Todo


class TodoRepository(ABC):
    @abstractmethod
    def list_all(self) -> List[Todo]:
        """Return all todos, newest first."""

    @abstractmethod
    def create(self, description: str, created_at: datetime) -> Todo:
        """Persist a new todo and return it with its generated id."""


class MongoTodoRepository(TodoRepository):
    COLLECTION_NAME = 'todos'

    def __init__(self, database: Database):
        self._collection: Collection = database[self.COLLECTION_NAME]

    def ensure_indexes(self) -> None:
        # list_all sorts by created_at; the index keeps that fast as data grows.
        # create_index is idempotent, so calling it on startup is safe.
        self._collection.create_index([('created_at', DESCENDING)])

    def list_all(self) -> List[Todo]:
        documents = self._collection.find().sort('created_at', DESCENDING)
        return [self._to_entity(document) for document in documents]

    def create(self, description: str, created_at: datetime) -> Todo:
        # BSON dates only store milliseconds. Truncate up front so the todo we
        # return here is identical to the one a later read returns.
        created_at = created_at.replace(microsecond=created_at.microsecond // 1000 * 1000)
        document = {'description': description, 'created_at': created_at}
        result = self._collection.insert_one(document)
        return Todo(id=str(result.inserted_id), description=description, created_at=created_at)

    @staticmethod
    def _to_entity(document: dict) -> Todo:
        return Todo(
            id=str(document['_id']),
            description=document['description'],
            created_at=document['created_at'],
        )
