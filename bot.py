import asyncio
import logging
import typing

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger
from aiogram_plugins import monkey_patch; monkey_patch(Dispatcher)

from middlewares.BotContextMiddleware import BotContextMiddleware

from plugins.ticket_system.ticket_system_plugin import ticket_plugin

from config import config


if __name__ == '__main__':
    API_TOKEN = config['BOT_TEST_TOKEN']

    loop = asyncio.get_event_loop()

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(BotContextMiddleware(dp))

    loop.run_until_complete(dp.register_plugin(ticket_plugin))

    executor.start_polling(dp, skip_updates=True)
