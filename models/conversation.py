import uuid
import datetime
import enum

class Conversation:
    def __init__(self, conversation_id: int, ticket_id: uuid.UUID, text: str, from_user_id: int, from_support: bool, created_at: datetime.datetime):
        self.conversation_id: int = conversation_id
        self.ticket_id: uuid.UUID = ticket_id
        self.text: str = text
        self.from_user_id: int = from_user_id
        self.is_from_support: bool = from_support
        self.created_at: datetime.datetime = created_at
    
    def __str__(self) -> str:
        return "Conv ticket_id {} from user {} is supp {}".format(self.ticket_id, self.from_user_id, self.is_from_support)
