import uuid
import datetime


class Ticket:
    def __init__(self, ticket_id: uuid.UUID, user_id: int, created_at: datetime.datetime, text: str):
        self.ticket_id: uuid.UUID = ticket_id
        self.user_id: int = user_id
        self.created_at: datetime.datetime= created_at
        self.text: str = text
    
    def __str__(self) -> str:
        return "Ticket {} from user {}".format(self.ticket_id, self.user_id)