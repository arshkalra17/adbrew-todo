from unittest import mock

from django.test import SimpleTestCase
from pymongo.errors import ServerSelectionTimeoutError
from rest_framework.test import APIClient

from todos.service import TodoService
from todos.tests.fakes import InMemoryTodoRepository
from todos.views import TodoListView


class TodoApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.service = TodoService(InMemoryTodoRepository())
        patcher = mock.patch.object(TodoListView, 'get_service', return_value=self.service)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_get_returns_empty_list_initially(self):
        response = self.client.get('/todos/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'todos': []})

    def test_post_creates_todo_and_get_returns_it(self):
        create = self.client.post('/todos/', {'description': 'Learn React'}, format='json')
        listing = self.client.get('/todos/')

        self.assertEqual(create.status_code, 201)
        self.assertEqual(create.json()['description'], 'Learn React')
        self.assertEqual(listing.json()['todos'], [create.json()])

    def test_url_works_without_trailing_slash(self):
        response = self.client.post('/todos', {'description': 'No slash'}, format='json')

        self.assertEqual(response.status_code, 201)

    def test_post_with_empty_description_returns_400(self):
        response = self.client.post('/todos/', {'description': '   '}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error']['field'], 'description')

    def test_post_with_non_object_body_returns_400(self):
        response = self.client.post('/todos/', ['not', 'an', 'object'], format='json')

        self.assertEqual(response.status_code, 400)

    def test_post_with_malformed_json_returns_400(self):
        response = self.client.post('/todos/', '{bad json', content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.json()['error'])

    def test_database_failure_returns_503_without_leaking_details(self):
        with mock.patch.object(self.service, 'list_todos', side_effect=ServerSelectionTimeoutError('mongo:27017 down')), \
                self.assertLogs('rest.exception_handler', level='ERROR'):
            response = self.client.get('/todos/')

        self.assertEqual(response.status_code, 503)
        self.assertNotIn('mongo:27017', response.json()['error']['message'])
