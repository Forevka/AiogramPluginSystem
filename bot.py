import asyncio
import logging
import typing

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger as loguru_logger

from aiogram_plugins import AiogramPlugin
import config
from controllers.db_controller import DBworker, create_db
from handlers.ticket_handlers import TicketHandlers
from middlewares.DBmiddleware import AddTicketDBMiddleware

from aiogram_plugins import monkey_patch,AiogramHandlerPack; monkey_patch(Dispatcher)

async def connect_to_db(dp: Dispatcher):
    dp['ticket_db_worker'] = await create_db(**config.db_ticket_settings)


if __name__ == '__main__':
    API_TOKEN = config.BOT_TEST_TOKEN

    loop = asyncio.get_event_loop()

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    def a(dp):
        print(1)

    ticket_plugin = AiogramPlugin('TicketSupportSystem')
    ticket_plugin.plug_middleware(AddTicketDBMiddleware)
    ticket_plugin.plug_handler(TicketHandlers)
    ticket_plugin.plug_custom_method(connect_to_db)

    loop.run_until_complete(dp.register_plugin(ticket_plugin))
    executor.start_polling(dp, skip_updates=True)
