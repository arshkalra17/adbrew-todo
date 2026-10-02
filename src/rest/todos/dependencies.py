"""Composition root: the one place that decides which concrete classes are used.

Views ask for a TodoService here instead of constructing Mongo objects
themselves, so the wiring can change without editing any view.
"""
from functools import lru_cache

from rest.mongo import get_database
from todos.repository import MongoTodoRepository
from todos.service import TodoService


@lru_cache(maxsize=None)
def get_todo_service() -> TodoService:
    repository = MongoTodoRepository(get_database())
    # Runs once per process. If Mongo is down, the error propagates (becoming a
    # 503) and lru_cache does not store the failure, so the next request retries.
    repository.ensure_indexes()
    return TodoService(repository)
