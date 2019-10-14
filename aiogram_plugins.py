import enum
from inspect import iscoroutinefunction, isfunction
import re
import typing

from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.mixins import DataMixin
from loguru import logger

def convert_to_cnake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class ConfigForPluginMiddleware(BaseMiddleware):
    pluginConfigs: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = {}

    def __init__(self):
        super(ConfigForPluginMiddleware, self).__init__()

    def get_config_data(self) -> typing.Dict[typing.Any, typing.Any]:
        return {config_name: cfg for config_name, cfg in ConfigForPluginMiddleware.pluginConfigs.items()}

    async def on_pre_process_message(self, message: types.Message, data: typing.Dict[typing.Any, typing.Any]):
        data.update(self.get_config_data())
    
    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: typing.Dict[typing.Any, typing.Any]):
        data.update(self.get_config_data())

class AiogramHandlerPack(DataMixin):
    @staticmethod
    def register(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any]) -> typing.Any:
        raise NotImplemented("Static method register need to be implemented")

AiogramHandlerPackType = typing.TypeVar('AiogramHandlerPackType', bound=AiogramHandlerPack)

class WhenToCall(enum.IntEnum):
    BEFORE_MIDDLEWARES = AT_START = 1
    BEFORE_HANDLERS = AFTER_MIDDLEWARES = 2
    AFTER_HANDLERS = AFTER_ALL = 3


class AiogramPlugin:
    config: typing.Dict[typing.Any, typing.Any]
    middlewares: typing.List[BaseMiddleware]
    handlers: typing.List[typing.Type[AiogramHandlerPack]] #[[Dispatcher, typing.Dict[typing.Any, typing.Any]], typing.Any]
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

        ConfigForPluginMiddleware.pluginConfigs.update({convert_to_cnake_case(self.name) + "_config": self.config})

        logger.debug(f'Initialised {self.name} plugin')

    async def plug(self, dp: Dispatcher):
        if ConfigForPluginMiddleware not in dp.middleware.applications:
            logger.debug(
                f'Config middleware not setuped, setuping')
            dp.middleware.setup(ConfigForPluginMiddleware())

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


def monkey_patch(Dispatcher):
    async def register_plugin(self, plugin: AiogramPlugin, **kwargs):
        await plugin.plug(self, **kwargs)

    Dispatcher.register_plugin = register_plugin
