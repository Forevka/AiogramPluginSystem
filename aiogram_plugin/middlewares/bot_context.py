import typing

from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware


class BotContextMiddleware(BaseMiddleware):
    def __init__(self, dp: Dispatcher):
        self.dp: Dispatcher = dp
        super(BotContextMiddleware, self).__init__()

    def bot_context_data(self) -> typing.Dict[typing.Any, typing.Any]:
        return {'bot': self.dp.bot}

    async def on_pre_process_message(self, message: types.Message, data: dict):
        data.update(self.bot_context_data())
    
    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: typing.Dict[typing.Any, typing.Any]):
        data.update(self.bot_context_data())
