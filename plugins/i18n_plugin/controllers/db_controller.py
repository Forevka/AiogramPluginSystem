import os
import typing
import uuid

from aiogram.utils.mixins import ContextInstanceMixin
import asyncpg
from loguru import logger

from ..models.user import User


class I18nDBworker(ContextInstanceMixin):
    conn: asyncpg.Connection

    def __init__(self, password: str, host: str, user: str = 'postgres', database: str = 'users',):
        self.password: str = password
        self.user: str = user
        self.database: str = database
        self.host: str = host
        #

    async def connect(self, migrate: bool = False) -> None:
        self.conn = await asyncpg.connect(user=self.user, password=self.password,
                                          database=self.database, host=self.host)

        if migrate:
            path_to_migrations = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'migrations'))
            for filename in os.listdir(path_to_migrations):
                if filename.endswith(".sql"):
                    sql_migration = open(os.path.join(
                        path_to_migrations, filename), 'r').read()
                    try:
                        res = await self.conn.execute(sql_migration)
                        logger.debug('Apply sql migration ' +
                                     str(filename) + "res: "+str(res))
                    except Exception as e:
                        logger.error(e)

    async def create_or_find_user(self, user_id: int, lang: str = 'en') -> typing.Optional[User]:
        sql_query = (
            """INSERT INTO users(user_id, lang) VALUES($1, $2) ON CONFLICT (user_id) DO UPDATE SET user_id = EXCLUDED.user_id RETURNING *""", user_id, lang)
        raw_user = await self.conn.fetchrow(*sql_query)
        logger.debug(raw_user)
        if raw_user:
            return User(**raw_user)

    async def update_user_lang(self, user_id: int, new_lang: str) -> int:
        sql_query = ("UPDATE users SET lang = $1 WHERE user_id = $2 RETURNING user_id",
                     new_lang, user_id)
        user_id = await self.conn.fetchval(*sql_query)
        return user_id


async def create_db(password: str, host: str, user: str = 'postgres', database: str = 'ticket_system', migrate: bool = False) -> I18nDBworker:
    db: I18nDBworker = I18nDBworker(password, host, user, database)
    await db.connect(migrate=migrate)
    return db
