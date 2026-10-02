from django.urls import re_path

from todos.views import TodoListView

# The trailing slash is optional. With a plain 'todos/' route, a POST to
# '/todos' (the URL in the task) would hit Django's APPEND_SLASH redirect,
# which cannot preserve a POST body and raises an error in DEBUG mode.
urlpatterns = [
    re_path(r'^todos/?$', TodoListView.as_view(), name='todo-list'),
]
