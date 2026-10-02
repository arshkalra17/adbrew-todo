from django.urls import re_path

from todos.views import TodoListView

# Optional trailing slash: APPEND_SLASH can't redirect a POST to '/todos' without losing its body.
urlpatterns = [
    re_path(r'^todos/?$', TodoListView.as_view(), name='todo-list'),
]
