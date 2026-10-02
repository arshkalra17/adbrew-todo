import logging

from pymongo.errors import PyMongoError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from rest.exceptions import InvalidInputError

logger = logging.getLogger(__name__)


def _error_response(message, status_code, field=None):
    body = {'error': {'message': message}}
    if field:
        body['error']['field'] = field
    return Response(body, status=status_code)


def _view_name(context):
    view = context.get('view')
    return type(view).__name__ if view is not None else 'unknown view'


def api_exception_handler(exc, context):
    if isinstance(exc, InvalidInputError):
        return _error_response(exc.message, status.HTTP_400_BAD_REQUEST, exc.field)

    if isinstance(exc, PyMongoError):
        logger.exception('Database error in %s', _view_name(context))
        return _error_response(
            'The database is currently unavailable. Please try again later.',
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        data = response.data
        detail = data.get('detail', data) if isinstance(data, dict) else data
        return _error_response(str(detail), response.status_code)

    logger.exception('Unhandled error in %s', _view_name(context))
    return _error_response(
        'Something went wrong on our side.', status.HTTP_500_INTERNAL_SERVER_ERROR
    )
