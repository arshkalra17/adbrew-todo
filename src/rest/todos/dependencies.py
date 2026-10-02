from functools import lru_cache

from rest.mongo import get_database
from todos.repository import MongoTodoRepository
from todos.service import TodoService


@lru_cache(maxsize=None)
def get_todo_service() -> TodoService:
    repository = MongoTodoRepository(get_database())
    repository.ensure_indexes()
    return TodoService(repository)
