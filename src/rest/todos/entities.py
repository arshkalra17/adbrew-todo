"""The Todo entity: what the rest of the code works with.

It is a plain dataclass, not a Django model. Mongo-specific details such as
ObjectId stay inside the repository, so views and services never see them.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Todo:
    id: str
    description: str
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }
