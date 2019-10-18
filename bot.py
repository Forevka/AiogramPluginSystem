import asyncio
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.handler import Handler

from aiogram_plugin import monkey_patch; monkey_patch(Dispatcher, Handler)
from config import config
from plugins.ticket_system.ticket_system_plugin import ticket_plugin;
from plugins.simple_echo.simple_echo_plugin import echo_plugin
#from plugins.broadcasting.broadcasting_plugin import broadcating_plugin


if __name__ == '__main__':
    API_TOKEN = config['BOT_TEST_TOKEN']

    loop = asyncio.get_event_loop()

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)


    #loop.run_until_complete(dp.register_plugin(ticket_plugin))
    loop.run_until_complete(dp.register_plugin(echo_plugin))
    #loop.run_until_complete(dp.register_plugin(broadcating_plugin))

    executor.start_polling(dp, skip_updates=True)
