from datetime import datetime, timedelta, timezone

import mongomock
from bson import ObjectId
from django.test import SimpleTestCase

from todos.repository import MongoTodoRepository

FIXED_TIME = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)


class MongoTodoRepositoryTests(SimpleTestCase):
    """Runs the real repository against mongomock, an in-memory Mongo fake."""

    def setUp(self):
        self.database = mongomock.MongoClient(tz_aware=True)['test_db']
        self.repository = MongoTodoRepository(self.database)

    def test_create_persists_document_and_returns_string_id(self):
        todo = self.repository.create('Learn Mongo', FIXED_TIME)

        stored = self.database['todos'].find_one({'_id': ObjectId(todo.id)})
        self.assertEqual(stored['description'], 'Learn Mongo')
        self.assertIsInstance(todo.id, str)

    def test_created_todo_matches_what_is_read_back(self):
        created = self.repository.create('Precise', FIXED_TIME.replace(microsecond=123456))

        [read_back] = self.repository.list_all()
        self.assertEqual(created, read_back)
        self.assertEqual(created.created_at.microsecond, 123000)

    def test_list_all_maps_documents_newest_first(self):
        self.repository.create('older', FIXED_TIME)
        self.repository.create('newer', FIXED_TIME + timedelta(minutes=5))

        todos = self.repository.list_all()

        self.assertEqual([todo.description for todo in todos], ['newer', 'older'])

    def test_ensure_indexes_creates_created_at_index(self):
        self.repository.ensure_indexes()

        index_keys = [index['key'] for index in self.database['todos'].index_information().values()]
        self.assertIn([('created_at', -1)], index_keys)
