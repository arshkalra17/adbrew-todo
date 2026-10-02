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
        self._collection.create_index([('created_at', DESCENDING)])

    def list_all(self) -> List[Todo]:
        documents = self._collection.find().sort('created_at', DESCENDING)
        return [self._to_entity(document) for document in documents]

    def create(self, description: str, created_at: datetime) -> Todo:
        # Mongo stores milliseconds only; truncate so the returned todo matches what GET reads back.
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
