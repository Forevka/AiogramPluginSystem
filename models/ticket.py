from models.conversation import Conversation
import typing
import uuid
import datetime
import enum

class TicketStatus(enum.Enum):
    NEW = 1
    ON_HOLD = 2
    ON_REVIEW = 3
    CLOSED = 4


class Ticket:
    conversations: typing.List[Conversation]

    def __init__(self, ticket_id: uuid.UUID, user_id: int, created_at: datetime.datetime, status: int, user_message_id):
        self.ticket_id: uuid.UUID = ticket_id
        self.user_id: int = user_id
        self.created_at: datetime.datetime = created_at
        self.status: TicketStatus = TicketStatus(status)
        self.user_message_id: int = user_message_id

        self.conversations = []
    
    def __str__(self) -> str:
        return "Ticket {} from user {} status {}".format(self.ticket_id, self.user_id, self.status)