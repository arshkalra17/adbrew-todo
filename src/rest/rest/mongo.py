"""MongoDB connection management.

MongoClient keeps its own connection pool and is thread-safe, so the
application should create exactly one and share it. It is created lazily
(on first use) so that importing this module never opens a connection,
which keeps imports cheap and lets tests run without a database.
"""
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
        # Return timezone-aware datetimes; pymongo returns naive ones by default.
        tz_aware=True,
    )


def get_database() -> Database:
    return get_client()[settings.MONGO['DB_NAME']]
