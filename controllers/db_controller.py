import typing

import asyncpg
import uuid
from loguru import logger

from models.ticket import Ticket
from aiogram.utils.mixins import ContextInstanceMixin


class DBworker(ContextInstanceMixin):
    conn: asyncpg.Connection

    def __init__(self, password: str, host: str, user: str = 'postgres', database: str = 'ticket_system',):
        self.password: str = password
        self.user: str = user
        self.database: str = database
        self.host: str = host
        #
    
    async def connect(self):
        self.conn = await asyncpg.connect(user=self.user, password=self.password,
                                 database=self.database, host=self.host)
    

    async def find_ticket(self, ticket_id: typing.Union[str, uuid.UUID]) -> Ticket:
        sql_query = "SELECT * FROM tickets WHERE ticket_id = '{}'".format(str(ticket_id))
        ticket = await self.conn.fetchrow(sql_query)
        logger.debug(ticket)
        return Ticket(**ticket)
        
    async def create_ticket(self, user_id: int, ticket_text) -> uuid.UUID:
        sql_query = ("""INSERT INTO tickets (user_id, text) 
                        VALUES($1, $2)
                        RETURNING ticket_id""", user_id, ticket_text)
        ticket_id = await self.conn.fetchval(*sql_query)
        logger.debug(ticket_id)
        return ticket_id




async def create_db(password: str, host: str, user: str = 'postgres', database: str = 'ticket_system') -> DBworker:
    db: DBworker = DBworker(password, host, user, database)
    await db.connect()
    return db


'''
async def run():
    conn = await asyncpg.connect(user='postgres', password='werdwerd',
                                    database='ticket_system', host='194.67.198.163')
    print(values)
    await conn.close()
'''
