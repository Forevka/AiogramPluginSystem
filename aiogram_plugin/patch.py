from inspect import getfullargspec

from loguru import logger

from .aiogram_plugin import AiogramPlugin
from .filters.mark_plugin_name import MarkPluginName
from .middlewares.bot_context import BotContextMiddleware
from .middlewares.config_to_plugins import ConfigForPluginMiddleware
from .utils.utils import convert_to_snake_case


def monkey_patch(Dispatcher, Handler):
    def _get_spec(func: callable):
        while hasattr(func, '__wrapped__'):  # Try to resolve decorated callbacks
            func = func.__wrapped__
        spec = getfullargspec(func)
        return spec

    def new_init(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            logger.debug('Dispatcher initiated, setuping Context middlewares')
            _setup_context_middlewares(self)
        return wrapper

    def _setup_context_middlewares(self):
        logger.debug(
            f'Setuping Config context middleware')
        self.middleware.setup(ConfigForPluginMiddleware())
        logger.debug(
            f'Setuping Bot to context middleware')
        self.middleware.setup(BotContextMiddleware(self))

    async def register_plugin(self, plugin: AiogramPlugin, **kwargs):
        AiogramPlugin.set_current(plugin)
        await plugin.plug(self, **kwargs)

    def register(self, handler, filters=None, index=None):
        """
        Register callback
        Filters can be awaitable or not.
        :param handler: coroutine
        :param filters: list of filters
        :param index: you can reorder handlers
        """
        from aiogram.dispatcher.filters import get_filters_spec

        if filters and not isinstance(filters, (list, tuple, set)):
            filters = [filters]

        plugin: AiogramPlugin = AiogramPlugin.get_current()
        if plugin:
            if filters:
                filters.append(MarkPluginName(
                    convert_to_snake_case(plugin.name)))
            else:
                filters = [MarkPluginName(convert_to_snake_case(plugin.name))]

        spec = _get_spec(handler)

        filters = get_filters_spec(self.dispatcher, filters)

        record = Handler.HandlerObj(
            handler=handler, spec=spec, filters=filters)
        if index is None:
            self.handlers.append(record)
        else:
            self.handlers.insert(index, record)

    Dispatcher.__init__ = new_init(Dispatcher.__init__)

    Dispatcher.register_plugin = register_plugin
    Handler.register = register
