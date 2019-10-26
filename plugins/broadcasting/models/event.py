from uuid import UUID

from datetime import datetime


class Event:
    def __init__(self, event_id: UUID, when_execute: datetime, text: str, created_by: int, created_datetime: datetime, edited_by: int, edited_datetime: datetime, status: int):
        self.event_id = event_id
        self.when_execute = when_execute
        self.text = text
        self.created_by = created_by
        self.created_datetime = created_datetime
        self.edited_by = edited_by
        self.edited_datetime = edited_datetime
        self.status = status