from calendar import month, monthrange
from dateutil.relativedelta import relativedelta
import typing
import uuid
from datetime import datetime, timedelta, date

from aiogram.utils.mixins import ContextInstanceMixin

import asyncpg
from loguru import logger

from ..models.event import Event
from uuid import UUID

def add_one_month(orig_date: date):
    new_year = orig_date.year
    new_month = orig_date.month + 1 # from 1 to 12 not 0 - 11
    if new_month > 12:
        new_year += 1
        new_month -= 12

    last_day_of_month = monthrange(new_year, new_month)[1]
    new_day = min(orig_date.day, last_day_of_month)

    return orig_date.replace(year=new_year, month=new_month, day=new_day)

class BroadcastingDBworker(ContextInstanceMixin):
    conn: asyncpg.Connection

    def __init__(self, password: str, host: str, user: str = 'postgres', database: str = 'broadcsting',):
        self.password: str = password
        self.user: str = user
        self.database: str = database
        self.host: str = host

    async def connect(self, migrate: bool = False) -> None:
        self.conn = await asyncpg.connect(user=self.user, password=self.password,
                                          database=self.database, host=self.host)
        
        if migrate:
            pass

    async def create_event(self, when_execute: datetime, text: str, created_by: int) -> UUID:
        sql_query = ("""INSERT INTO events (when_execute, text, created_by, edited_by, edited_datetime) 
                        VALUES($1, $2, $3, $4, $5)
                        RETURNING event_id""", when_execute, text, created_by, created_by, datetime.now())
        event_id = await self.conn.fetchval(*sql_query)
        logger.debug(event_id)
        return event_id
    
    async def find_event_for_day(self, this_date: date, page: int = 1, per_page: int = 5,) -> typing.Tuple[bool, typing.List[Event]]:
        end_date = (this_date + timedelta(days=1))
        sql_query = (
            "SELECT * FROM events WHERE when_execute >= $1 AND when_execute < $2 ORDER BY created_datetime DESC LIMIT $3 OFFSET $4", 
                    this_date, end_date, per_page + 1, (page-1) * per_page)
        raw_events = await self.conn.fetch(*sql_query)
        if raw_events:
            return (len(raw_events) == (per_page + 1), [Event(**i) for i in raw_events])
        return (False, [])
    
    async def find_events_for_month(self, this_date: date) -> typing.List[int]:
        this_date: date = date(this_date.year, this_date.month, 1)
        end_date = add_one_month(this_date)
        sql_query = (
            "SELECT EXTRACT(DAY FROM when_execute) FROM events WHERE when_execute >= $1 AND when_execute < $2 ORDER BY created_datetime", 
                    this_date, end_date,)
        days = await self.conn.fetch(*sql_query)
        return [int(i['date_part']) for i in days]
    
    async def find_event_by_id(self, event_id: UUID) -> typing.Optional[Event]:
        sql_query = (
            "SELECT * FROM events WHERE event_id = $1", str(event_id))
        raw_event = await self.conn.fetchrow(*sql_query)
        if raw_event:
            return Event(**raw_event)
    
    async def update_text_in_event(self, event_id: UUID, text: str, updated_by: int) -> typing.Optional[Event]:
        sql_query = (
            "UPDATE events SET text = $2, edited_by = $3, edited_datetime = $4 WHERE event_id = $1 RETURNING *", str(event_id), text, updated_by, datetime.now())
        raw_event = await self.conn.fetchrow(*sql_query)
        if raw_event:
            return Event(**raw_event)
    
    async def update_execute_time_in_event(self, event_id: UUID, new_time: datetime, updated_by: int) -> typing.Optional[Event]:
        sql_query = (
            "UPDATE events SET when_execute = $2, edited_by = $3, edited_datetime = $4 WHERE event_id = $1 RETURNING *", str(event_id), new_time, updated_by, datetime.now())
        raw_event = await self.conn.fetchrow(*sql_query)
        if raw_event:
            return Event(**raw_event)
    
    async def delete_event_by_id(self, event_id: UUID) -> bool:
        sql_query = (
            "DELETE FROM events WHERE event_id = $1 RETURNING *", str(event_id))
        raw_event = await self.conn.fetchrow(*sql_query)
        if raw_event:
            return True
        return False
    
    async def get_latest_events(self,) -> typing.List[Event]:
        sql_query = (
            "SELECT * from events WHERE when_execute<=CURRENT_TIMESTAMP + interval '1 hour' AND status = 1 ORDER BY when_execute ASC",)
        raw_events = await self.conn.fetch(*sql_query)
        if raw_events:
            return [Event(**i) for i in raw_events]
        return []

    async def update_event_status_by_id(self, event_id: UUID, new_status: int, updated_by: int) -> typing.Optional[Event]:
        sql_query = (
            "UPDATE events SET status = $2, edited_by = $3, edited_datetime = $4 WHERE event_id = $1 RETURNING *", str(event_id), new_status, updated_by, datetime.now())
        raw_event = await self.conn.fetchrow(*sql_query)
        if raw_event:
            return Event(**raw_event)

async def create_db(password: str, host: str, user: str = 'postgres', database: str = 'broadcsting', migrate: bool = False) -> BroadcastingDBworker:
    db: BroadcastingDBworker = BroadcastingDBworker(password, host, user, database)
    await db.connect(migrate = migrate)
    return db
