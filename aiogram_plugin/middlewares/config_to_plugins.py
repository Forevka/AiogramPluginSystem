import typing

from aiogram import types
from aiogram.dispatcher.filters.filters import Filter
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger


class ConfigForPluginMiddleware(BaseMiddleware):
    pluginConfigs: typing.Dict[str, typing.Dict[typing.Any, typing.Any]] = {}

    def __init__(self):
        super(ConfigForPluginMiddleware, self).__init__()

    def get_config_data(self, plugin_name: str) -> typing.Dict[typing.Any, typing.Any]:
        plugin_full_config: dict = ConfigForPluginMiddleware.pluginConfigs.get(
            plugin_name + '_config', {})
        return {'plugin_config': plugin_full_config.get('to_handlers', plugin_full_config)}

    async def on_process_message(self, message: types.Message, data: typing.Dict[typing.Any, typing.Any]):
        if data['_plugin_name']:
            data.update(self.get_config_data(data['_plugin_name']))

    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: typing.Dict[typing.Any, typing.Any]):
        if data['_plugin_name']:
            data.update(self.get_config_data(data['_plugin_name']))
