from datetime import datetime
from typing import List

from todos.entities import Todo
from todos.repository import TodoRepository


class InMemoryTodoRepository(TodoRepository):
    """Test double that honours the same contract as MongoTodoRepository."""

    def __init__(self):
        self._todos: List[Todo] = []

    def list_all(self) -> List[Todo]:
        return sorted(self._todos, key=lambda todo: todo.created_at, reverse=True)

    def create(self, description: str, created_at: datetime) -> Todo:
        todo = Todo(id=str(len(self._todos) + 1), description=description, created_at=created_at)
        self._todos.append(todo)
        return todo
