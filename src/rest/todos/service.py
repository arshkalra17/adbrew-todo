from datetime import datetime, timezone
from typing import Any, Callable, List

from rest.exceptions import InvalidInputError
from todos.entities import Todo
from todos.repository import TodoRepository

MAX_DESCRIPTION_LENGTH = 500


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TodoService:
    def __init__(self, repository: TodoRepository, clock: Callable[[], datetime] = _utc_now):
        self._repository = repository
        self._clock = clock

    def list_todos(self) -> List[Todo]:
        return self._repository.list_all()

    def create_todo(self, description: Any) -> Todo:
        cleaned = self._validate_description(description)
        return self._repository.create(description=cleaned, created_at=self._clock())

    @staticmethod
    def _validate_description(description: Any) -> str:
        if not isinstance(description, str):
            raise InvalidInputError('Description must be a string.', field='description')

        cleaned = description.strip()
        if not cleaned:
            raise InvalidInputError('Description cannot be empty.', field='description')
        if len(cleaned) > MAX_DESCRIPTION_LENGTH:
            raise InvalidInputError(
                'Description cannot be longer than {} characters.'.format(MAX_DESCRIPTION_LENGTH),
                field='description',
            )
        return cleaned
