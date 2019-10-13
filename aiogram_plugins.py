import enum
from inspect import iscoroutinefunction, isfunction
import typing

from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger


class AiogramHandlerPack:
    @staticmethod
    def register(dp: Dispatcher) -> typing.Any:
        raise NotImplemented("Static method register need to be implemented")


class WhenToCall(enum.IntEnum):
    BEFORE_MIDDLEWARES = AT_START = 1
    BEFORE_HANDLERS = AFTER_MIDDLEWARES = 2
    AFTER_HANDLERS = AFTER_ALL = 3


class AiogramPlugin:
    middlewares: typing.List[BaseMiddleware]
    handlers: typing.List[AiogramHandlerPack]
    custom_methods_at_start: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[
        None], typing.Awaitable], typing.Callable]]]
    custom_methods_before_handlers: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[
        None], typing.Awaitable], typing.Callable]]]
    custom_methods_after_all: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[
        None], typing.Awaitable], typing.Callable]]]

    def __init__(self, name: str):
        self.name: str = name
        self.middlewares = []
        self.handlers = []

        self.custom_methods_at_start = []
        self.custom_methods_before_handlers = []
        self.custom_methods_after_all = []

        logger.debug(f'Initialised {self.name} plugin')

    async def plug(self, dp: Dispatcher):
        logger.debug(
            f'Start launching custom methods AT START by plugin {self.name}')
        for iscoro, method in self.custom_methods_at_start:
            if iscoro:
                await method(dp)
            else:
                method(dp)
        logger.debug(
            f'Successfully launched custom methods AT START by plugin {self.name}')


        logger.debug(
            f'Start setuping middlewares to dispatcher by plugin {self.name}')
        for midd in self.middlewares:
            logger.debug(f'Setuping {midd.__name__} by plugin {self.name}')
            dp.middleware.setup(midd(dp))
            logger.debug(f'Setuped {midd.__name__} by plugin {self.name}')

        logger.debug(f'Successfully setuped middlewares by plugin {self.name}')

        logger.debug(
            f'Start launching custom methods AT MIDDLE by plugin {self.name}')
        for iscoro, method in self.custom_methods_before_handlers:
            if iscoro:
                await method(dp)
            else:
                method(dp)
        logger.debug(
            f'Successfully launched custom methods AT MIDDLE by plugin {self.name}')

        logger.debug(
            f'Start registering handlers to dispatcher by plugin {self.name}')

        for handler_pack in self.handlers:
            logger.debug(
                f'Registering {handler_pack.__name__} by plugin {self.name}')
            handler_pack.register(dp)
            logger.debug(
                f'Registered {handler_pack.__name__} by plugin {self.name}')

        logger.debug(f'Successfully registered handlers by plugin {self.name}')

        logger.debug(
            f'Start launching custom methods AT END by plugin {self.name}')
        for iscoro, method in self.custom_methods_after_all:
            if iscoro:
                await method(dp)
            else:
                method(dp)
        logger.debug(
            f'Successfully launched custom methods AT END by plugin {self.name}')

    def plug_middleware(self, middleware: BaseMiddleware) -> 'AiogramPlugin':
        self.middlewares.append(middleware)
        logger.debug(
            f'Plugged {middleware.__name__} middleware to {self.name} plugin')
        return self

    def plug_handler(self, handler_pack: AiogramHandlerPack,) -> 'AiogramPlugin':
        self.handlers.append(handler_pack)
        logger.debug(
            f'Plugged {handler_pack.__name__} handlers to {self.name} plugin')
        return self

    def plug_custom_method(self, method: typing.Union[typing.Callable[[None], typing.Awaitable], typing.Callable], when_to_call: WhenToCall = WhenToCall.AFTER_ALL):
        if isfunction(method):
            if when_to_call == WhenToCall.AT_START or when_to_call == WhenToCall.BEFORE_MIDDLEWARES:
                self.custom_methods_at_start.append(
                    (iscoroutinefunction(method), method))
                logger.debug(
                    f'Plugged {method.__name__} method to {self.name} plugin AT START')
            elif when_to_call == WhenToCall.BEFORE_HANDLERS or when_to_call == WhenToCall.AFTER_MIDDLEWARES:
                self.custom_methods_before_handlers.append(
                    (iscoroutinefunction(method), method))
                logger.debug(
                    f'Plugged {method.__name__} method to {self.name} plugin AT MIDDLE OF PROCESS')
            else:
                self.custom_methods_after_all.append(
                    (iscoroutinefunction(method), method))
                logger.debug(
                    f'Plugged {method.__name__} method to {self.name} plugin AT END')
        else:
            logger.debug(
                f'Can`t plugg {repr(method)} to {self.name} need to be callable')


def monkey_patch(Dispatcher):
    async def register_plugin(self, plugin: AiogramPlugin, **kwargs):
        await plugin.plug(self, **kwargs)

    Dispatcher.register_plugin = register_plugin
