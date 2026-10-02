"""Root URL configuration. Each app owns its routes and is included here."""
from django.urls import include, path

urlpatterns = [
    path('', include('todos.urls')),
]
