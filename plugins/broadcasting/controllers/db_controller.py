import typing
import uuid
import datetime

from aiogram.utils.mixins import ContextInstanceMixin

import asyncpg
from loguru import logger

from ..models.event import Event
from uuid import UUID


class BroadcstingDBworker(ContextInstanceMixin):
    conn: asyncpg.Connection

    def __init__(self, password: str, host: str, user: str = 'postgres', database: str = 'broadcsting',):
        self.password: str = password
        self.user: str = user
        self.database: str = database
        self.host: str = host

    async def connect(self, migrate: bool = False) -> None:
        self.conn = await asyncpg.connect(user=self.user, password=self.password,
                                          database=self.database, host=self.host)
        
        '''if migrate:
            sql_create_tickets_table = open('plugins/ticket_system/migrations/tickets.sql', 'r').read()
            sql_create_conversations_table = open('plugins/ticket_system/migrations/conversation.sql', 'r').read()
            try:
                res = await self.conn.execute(sql_create_tickets_table)
                logger.debug('Migrated tickets table with ' + str(res))
                await self.conn.execute(sql_create_conversations_table)
                logger.debug('Migrated conversation table with ' + str(res))
            except Exception as e:
                logger.error(e)'''

    async def create_event(self, when_execute: datetime, text: str, created_by: int) -> UUID:
        sql_query = ("""INSERT INTO events (when_execute, text, created_by) 
                        VALUES($1, $2, $3)
                        RETURNING event_id""", when_execute, text, created_by)
        event_id = await self.conn.fetchval(*sql_query)
        logger.debug(event_id)
        return event_id
    
    async def find_event_for_day(self, year: int, month: int, day: int):
        start_date: str = datetime.date(year, month, day).strftime('YYYY-mm-dd')
        end_date: str = (datetime.date(year, month, day) + datetime.timedelta(days=1)).strftime('YYYY-mm-dd')
        print(start_date, end_date)
        sql_query = (
            "SELECT * FROM events WHERE when_execute >= $1 AND when_execute < $2", start_date, end_date)
        convers = await self.conn.fetch(*sql_query)
        print(convers)
    
    async def find_event_for_month(self, year: int, month: int):
        pass
    
    async def find_event_by_id(self, event_id: UUID):
        sql_query = (
            "SELECT * FROM events WHERE event_id = $1", str(event_id))
        raw_event = await self.conn.fetchrow(*sql_query)
        if raw_event:
            return Event(**raw_event)


async def create_db(password: str, host: str, user: str = 'postgres', database: str = 'broadcsting', migrate: bool = False) -> BroadcstingDBworker:
    db: BroadcstingDBworker = BroadcstingDBworker(password, host, user, database)
    await db.connect(migrate = migrate)
    return db
