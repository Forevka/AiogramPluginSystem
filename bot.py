import logging
import typing
import asyncio
from inspect import iscoroutinefunction, isfunction

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares import BaseMiddleware
import enum

import config
from controllers.db_controller import DBworker, create_db
from handlers.ticket_handlers import TicketHandlers, AiogramHandlerPack
from middlewares.DBmiddleware import AddTicketDBMiddleware
from loguru import logger as loguru_logger


async def on_startup(dp: Dispatcher):
    dp['ticket_db_worker'] = await create_db(**config.db_ticket_settings)

class WhenToCall(enum.IntEnum):
    BEFORE_MIDDLEWARES = AT_START = 1
    BEFORE_HANDLERS = AFTER_MIDDLEWARES = 2
    AFTER_HANDLERS = AFTER_ALL = 3

class AiogramPlugin:
    middlewares: typing.List[BaseMiddleware]
    handlers: typing.List[AiogramHandlerPack]
    custom_methods_at_start: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[None], typing.Awaitable], typing.Callable]]]
    custom_methods_before_handlers: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[None], typing.Awaitable], typing.Callable]]]
    custom_methods_after_all: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[None], typing.Awaitable], typing.Callable]]]

    def __init__(self, name: str):
        self.name: str = name
        self.middlewares = []
        self.handlers = []

        self.custom_methods_at_start = []
        self.custom_methods_before_handlers = []
        self.custom_methods_after_all = []

        loguru_logger.debug(f'Initialised {self.name} plugin')

    async def plug(self, dp: Dispatcher):
        loguru_logger.debug(f'Start setuping middlewares to dispatcher by plugin {self.name}')

        for iscoro, method in self.custom_methods_at_start:
            if iscoro:
                await method(dp)
            else:
                method(dp)

        for midd in self.middlewares:
            loguru_logger.debug(f'Setuping {midd.__name__} by plugin {self.name}')
            dp.middleware.setup(midd(dp))
            loguru_logger.debug(f'Setuped {midd.__name__} by plugin {self.name}')

        loguru_logger.debug(f'Successfylly setuped middlewares by plugin {self.name}')

        for iscoro, method in self.custom_methods_before_handlers:
            if iscoro:
                await method(dp)
            else:
                method(dp)

        loguru_logger.debug(f'Start registering handlers to dispatcher by plugin {self.name}')

        for handler_pack in self.handlers:
            loguru_logger.debug(f'Registering {handler_pack.__name__} by plugin {self.name}')
            handler_pack.register(dp)
            loguru_logger.debug(f'Registered {handler_pack.__name__} by plugin {self.name}')

        loguru_logger.debug(f'Successfully registered handlers by plugin {self.name}')

        for iscoro, method in self.custom_methods_after_all:
            if iscoro:
                await method(dp)
            else:
                method(dp)

    def plug_middleware(self, middleware: BaseMiddleware) -> 'AiogramPlugin':
        self.middlewares.append(middleware)
        loguru_logger.debug(f'Plugged {middleware.__name__} middleware to {self.name} plugin')
        return self

    def plug_handler(self, handler_pack: AiogramHandlerPack,) -> 'AiogramPlugin':
        self.handlers.append(handler_pack)
        loguru_logger.debug(f'Plugged {handler_pack.__name__} handlers to {self.name} plugin')
        return self
    
    def plug_custom_method(self, method: typing.Union[typing.Callable[[None], typing.Awaitable], typing.Callable], when_to_call: WhenToCall = WhenToCall.AFTER_ALL):
        if isfunction(method):
            if when_to_call == WhenToCall.AT_START or when_to_call == WhenToCall.BEFORE_MIDDLEWARES:
                self.custom_methods_at_start.append((iscoroutinefunction(method), method))
                loguru_logger.debug(f'Plugged {method.__name__} method to {self.name} plugin AT START')
            elif when_to_call == WhenToCall.BEFORE_HANDLERS or when_to_call == WhenToCall.AFTER_MIDDLEWARES:
                self.custom_methods_before_handlers.append((iscoroutinefunction(method), method))
                loguru_logger.debug(f'Plugged {method.__name__} method to {self.name} plugin AT MIDDLE OF PROCESS')
            else:
                self.custom_methods_after_all.append((iscoroutinefunction(method), method))
                loguru_logger.debug(f'Plugged {method.__name__} method to {self.name} plugin AT END')
        else:
            loguru_logger.debug(f'Can`t plugg {repr(method)} to {self.name} need to be callable')


async def register_plugin(self, plugin: AiogramPlugin, **kwargs):
    await plugin.plug(self, **kwargs)


Dispatcher.register_plugin = register_plugin

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
    ticket_plugin.plug_custom_method(on_startup)
    ticket_plugin.plug_custom_method(a)
    ticket_plugin.plug_custom_method('variable') #can`t plug this 
    loop.run_until_complete(dp.register_plugin(ticket_plugin))
    executor.start_polling(dp, skip_updates=True)
