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
