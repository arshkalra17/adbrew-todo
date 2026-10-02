from functools import lru_cache

from django.conf import settings
from pymongo import MongoClient
from pymongo.database import Database


@lru_cache(maxsize=None)
def get_client() -> MongoClient:
    config = settings.MONGO
    return MongoClient(
        host=config['HOST'],
        port=config['PORT'],
        serverSelectionTimeoutMS=config['SERVER_SELECTION_TIMEOUT_MS'],
        tz_aware=True,
    )


def get_database() -> Database:
    return get_client()[settings.MONGO['DB_NAME']]
