import typing
import os
import uuid

from aiogram.utils.mixins import ContextInstanceMixin
import asyncpg
from loguru import logger

from ..models.conversation import Conversation
from ..models.ticket import Ticket, TicketStatus


class TicketDBworker(ContextInstanceMixin):
    conn: asyncpg.Connection

    def __init__(self, password: str, host: str, user: str = 'postgres', database: str = 'ticket_system',):
        self.password: str = password
        self.user: str = user
        self.database: str = database
        self.host: str = host
        #

    async def connect(self, migrate: bool = False) -> None:
        self.conn = await asyncpg.connect(user=self.user, password=self.password,
                                          database=self.database, host=self.host)
        
        if migrate:
            path_to_migrations = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'migrations'))
            for filename in os.listdir(path_to_migrations):
                if filename.endswith(".sql"): 
                    sql_migration = open(os.path.join(path_to_migrations, filename), 'r').read()
                    try:
                        res = await self.conn.execute(sql_migration)
                        logger.debug('Apply sql migration ' + str(filename) + "res: "+str(res))
                    except Exception as e:
                        logger.error(e)

    async def add_conversation(self, text: str, ticket_id: typing.Union[str, uuid.UUID], from_user_id: int, from_support: bool, message_id: typing.Optional[int], reply_message_id: typing.Optional[int]) -> uuid.UUID:
        sql_query = ("""INSERT INTO conversation (text, ticket_id, from_user_id, from_support, message_id, reply_message_id) 
                        VALUES($1, $2, $3, $4, $5, $6)
                        RETURNING conversation_id""", text, str(ticket_id), from_user_id, from_support, message_id, reply_message_id)
        conv_id = await self.conn.fetchval(*sql_query)
        logger.debug(conv_id)
        return conv_id

    async def find_conversations(self, ticket_id: typing.Union[str, uuid.UUID]) -> typing.List[Conversation]:
        sql_query = (
            "SELECT * FROM conversation WHERE ticket_id = $1 ORDER BY created_at DESC", str(ticket_id))
        convers = await self.conn.fetch(*sql_query)
        return [Conversation(**i) for i in convers]

    async def update_ticket_status(self, ticket_id: typing.Union[str, uuid.UUID], new_status: TicketStatus) -> bool:
        sql_query = ("UPDATE tickets SET status = $1 WHERE ticket_id = $2",
                     new_status.value, str(ticket_id))
        ticket_id = await self.conn.fetchval(*sql_query)
        return True

    async def find_ticket_by_message_reply_id(self, user_id: int, reply_id: int) -> typing.Optional[Ticket]:
        sql_query = ("""SELECT t2.*
                        FROM conversation as t1
                        INNER JOIN tickets as t2 on t2.user_id = $1 and t1.reply_message_id = $2""", user_id, reply_id)
        raw_ticket = await self.conn.fetchrow(*sql_query)
        if raw_ticket:
            return Ticket(**raw_ticket)

    async def find_tickets(self, page=1, per_page=5) -> typing.Tuple[bool, typing.List[Ticket]]:
        sql_query = ("SELECT * FROM tickets ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                     per_page + 1, (page-1) * per_page)
        tickets = await self.conn.fetch(*sql_query)
        return (len(tickets) == (per_page + 1), [Ticket(**i) for i in tickets[:per_page]])

    async def find_ticket(self, ticket_id: typing.Union[str, uuid.UUID]) -> typing.Optional[Ticket]:
        sql_query = ("SELECT * FROM tickets WHERE ticket_id = $1",
                     str(ticket_id))
        raw_ticket = await self.conn.fetchrow(*sql_query)
        logger.debug(raw_ticket)
        if raw_ticket:
            ticket = Ticket(**raw_ticket)
            ticket.conversations.extend(await self.find_conversations(ticket.ticket_id))
            return ticket

    async def create_ticket(self, user_id: int, ticket_text: str, user_message_id: int) -> uuid.UUID:
        sql_query = ("""INSERT INTO tickets (user_id) 
                        VALUES($1)
                        RETURNING ticket_id""", user_id)
        ticket_id = await self.conn.fetchval(*sql_query)
        logger.debug(ticket_id)
        await self.add_conversation(ticket_text, ticket_id, user_id, False, user_message_id, None)
        return ticket_id


async def create_db(password: str, host: str, user: str = 'postgres', database: str = 'ticket_system', migrate: bool = False) -> TicketDBworker:
    db: TicketDBworker = TicketDBworker(password, host, user, database)
    await db.connect(migrate = migrate)
    return db
