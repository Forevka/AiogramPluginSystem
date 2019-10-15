from inspect import iscoroutinefunction, isfunction
import typing

from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.mixins import ContextInstanceMixin, DataMixin
from loguru import logger

from .meta_handler_pack import AiogramHandlerPack
from .middlewares.config_to_plugins import ConfigForPluginMiddleware
from .middlewares.bot_context import BotContextMiddleware
from .utils.utils import WhenToCall, convert_to_snake_case


class AiogramPlugin(ContextInstanceMixin, DataMixin):
    plugins: typing.List[str] = []
    config: typing.Dict[typing.Any, typing.Any]
    middlewares: typing.List[BaseMiddleware]
    handlers: typing.List[typing.Type[AiogramHandlerPack]]
    custom_methods_at_start: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[Dispatcher, typing.Dict[typing.Any, typing.Any]], typing.Any]]]]
    custom_methods_before_handlers: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[Dispatcher, typing.Dict[typing.Any, typing.Any]], typing.Any]]]]
    custom_methods_after_all: typing.List[typing.Tuple[int, typing.Union[typing.Callable[[Dispatcher, typing.Dict[typing.Any, typing.Any]], typing.Any]]]]

    def __init__(self, name: str, config: typing.Dict[typing.Any, typing.Any] = {}):
        self.name: str = name
        self.config = config
        self.middlewares = []
        self.handlers = []

        self.custom_methods_at_start = []
        self.custom_methods_before_handlers = []
        self.custom_methods_after_all = []

        if self.name in AiogramPlugin.plugins:
            raise AttributeError(f'Plugin {self.name} already exists')

        AiogramPlugin.plugins.append(self.name)
        ConfigForPluginMiddleware.pluginConfigs.update({convert_to_snake_case(self.name) + "_config": self.config})

        logger.debug(f'Initialised {self.name} plugin')

    async def plug(self, dp: Dispatcher):
        AiogramPlugin.get_current().data['_plugin_name'] = self.name
        if ConfigForPluginMiddleware not in dp.middleware.applications:
            logger.debug(
                f'Config middleware not setuped, setuping')
            dp.middleware.setup(ConfigForPluginMiddleware())
        if BotContextMiddleware not in dp.middleware.applications:
            logger.debug(
                f'Bot to context middleware not setuped, setuping')
            dp.middleware.setup(BotContextMiddleware(dp))

        logger.debug(
            f'Start launching custom methods AT START by plugin {self.name}')
        for iscoro, method in self.custom_methods_at_start:
            if iscoro:
                await method(dp, self.config)
            else:
                method(dp, self.config)
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
                await method(dp, self.config)
            else:
                method(dp, self.config)
        logger.debug(
            f'Successfully launched custom methods AT MIDDLE by plugin {self.name}')

        logger.debug(
            f'Start registering handlers to dispatcher by plugin {self.name}')

        for handler_pack in self.handlers:
            logger.debug(
                f'Registering {handler_pack.__name__} by plugin {self.name}')
            handler_pack.register(dp, self.config)
            logger.debug(
                f'Registered {handler_pack.__name__} by plugin {self.name}')

        logger.debug(f'Successfully registered handlers by plugin {self.name}')

        logger.debug(
            f'Start launching custom methods AT END by plugin {self.name}')
        for iscoro, method in self.custom_methods_after_all:
            if iscoro:
                await method(dp, self.config)
            else:
                method(dp, self.config)
        logger.debug(
            f'Successfully launched custom methods AT END by plugin {self.name}')

    def plug_middleware(self, middleware: BaseMiddleware) -> 'AiogramPlugin':
        self.middlewares.append(middleware)
        logger.debug(
            f'Plugged {middleware.__name__} middleware to {self.name} plugin')
        return self

    def plug_handler(self, handler_pack: typing.Type[AiogramHandlerPack],) -> 'AiogramPlugin':
        self.handlers.append(handler_pack)
        logger.debug(
            f'Plugged {handler_pack.__name__} handlers to {self.name} plugin')
        return self

    def plug_custom_method(self, method: typing.Union[typing.Callable[[Dispatcher, typing.Dict[typing.Any, typing.Any]], typing.Any]], when_to_call: WhenToCall = WhenToCall.AFTER_ALL):
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
