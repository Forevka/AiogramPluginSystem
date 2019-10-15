import typing

from aiogram.dispatcher.filters.filters import Filter
from loguru import logger


class MarkPluginName(Filter):
    def __init__(self, plugin_name: str):
        self.plugin_name: str = plugin_name

    async def check(self, object: typing.Any):
        return {"_plugin_name": self.plugin_name}
