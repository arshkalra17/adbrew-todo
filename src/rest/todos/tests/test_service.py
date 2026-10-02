from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from rest.exceptions import InvalidInputError
from todos.service import MAX_DESCRIPTION_LENGTH, TodoService
from todos.tests.fakes import InMemoryTodoRepository

FIXED_TIME = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


class TodoServiceTests(SimpleTestCase):
    def setUp(self):
        self.repository = InMemoryTodoRepository()
        self.service = TodoService(self.repository, clock=lambda: FIXED_TIME)

    def test_create_todo_strips_whitespace_and_sets_timestamp(self):
        todo = self.service.create_todo('  Learn Docker  ')

        self.assertEqual(todo.description, 'Learn Docker')
        self.assertEqual(todo.created_at, FIXED_TIME)
        self.assertEqual(self.repository.list_all(), [todo])

    def test_create_todo_rejects_invalid_descriptions(self):
        invalid_inputs = [None, 42, ['a list'], '', '   ', 'x' * (MAX_DESCRIPTION_LENGTH + 1)]

        for value in invalid_inputs:
            with self.subTest(value=value):
                with self.assertRaises(InvalidInputError) as context:
                    self.service.create_todo(value)
                self.assertEqual(context.exception.field, 'description')

        self.assertEqual(self.repository.list_all(), [])

    def test_create_todo_accepts_description_at_max_length(self):
        todo = self.service.create_todo('x' * MAX_DESCRIPTION_LENGTH)

        self.assertEqual(len(todo.description), MAX_DESCRIPTION_LENGTH)

    def test_list_todos_returns_newest_first(self):
        times = iter([FIXED_TIME, FIXED_TIME + timedelta(minutes=1)])
        service = TodoService(self.repository, clock=lambda: next(times))
        older = service.create_todo('first')
        newer = service.create_todo('second')

        self.assertEqual(service.list_todos(), [newer, older])
