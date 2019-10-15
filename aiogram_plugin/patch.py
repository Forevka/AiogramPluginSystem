from inspect import getfullargspec

from .aiogram_plugin import AiogramPlugin
from .filters.mark_plugin_name import MarkPluginName
from .utils.utils import convert_to_snake_case


def monkey_patch(Dispatcher, Handler):
    async def register_plugin(self, plugin: AiogramPlugin, **kwargs):
        AiogramPlugin.set_current(plugin)
        await plugin.plug(self, **kwargs)

    def _get_spec(func: callable):
        while hasattr(func, '__wrapped__'):  # Try to resolve decorated callbacks
            func = func.__wrapped__
        spec = getfullargspec(func)
        return spec

    def register(self, handler, filters=None, index=None):
        """
        Register callback
        Filters can be awaitable or not.
        :param handler: coroutine
        :param filters: list of filters
        :param index: you can reorder handlers
        """
        from aiogram.dispatcher.filters import get_filters_spec
        plugin: AiogramPlugin = AiogramPlugin.get_current()
        if plugin:
            if filters:
                filters.append(MarkPluginName(
                    convert_to_snake_case(plugin.name)))
            else:
                filters = [MarkPluginName(convert_to_snake_case(plugin.name))]

        spec = _get_spec(handler)

        if filters and not isinstance(filters, (list, tuple, set)):
            filters = [filters]

        filters = get_filters_spec(self.dispatcher, filters)

        record = Handler.HandlerObj(
            handler=handler, spec=spec, filters=filters)
        if index is None:
            self.handlers.append(record)
        else:
            self.handlers.insert(index, record)

    Dispatcher.register_plugin = register_plugin
    Handler.register = register
