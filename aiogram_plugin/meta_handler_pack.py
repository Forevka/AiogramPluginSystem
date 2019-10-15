import typing

from aiogram import Dispatcher
from aiogram.utils.mixins import DataMixin
from loguru import logger


class AiogramHandlerPack(DataMixin):
    @staticmethod
    def register(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any]) -> bool:
        raise NotImplemented("Static method register need to be implemented")
