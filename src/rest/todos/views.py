"""HTTP layer for todos.

Views only translate between HTTP and the service: read the request, call
the service, shape the response. Validation lives in the service, and error
responses are produced centrally by rest/exception_handler.py.
"""
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from rest.exceptions import InvalidInputError
from todos.dependencies import get_todo_service
from todos.service import TodoService


class TodoListView(APIView):
    parser_classes = [JSONParser]

    def get_service(self) -> TodoService:
        # A separate method so tests can substitute a service backed by fake storage.
        return get_todo_service()

    def get(self, request):
        todos = self.get_service().list_todos()
        return Response({'todos': [todo.to_dict() for todo in todos]}, status=status.HTTP_200_OK)

    def post(self, request):
        if not isinstance(request.data, dict):
            raise InvalidInputError('Request body must be a JSON object.')

        todo = self.get_service().create_todo(request.data.get('description'))
        return Response(todo.to_dict(), status=status.HTTP_201_CREATED)
