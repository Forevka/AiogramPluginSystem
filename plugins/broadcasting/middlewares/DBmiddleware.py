import typing

from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware


class AddBroadcastDBMiddleware(BaseMiddleware):
    def __init__(self, dp: Dispatcher):
        self.dp: Dispatcher = dp
        super(AddBroadcastDBMiddleware, self).__init__()

    def db_data(self) -> typing.Dict[typing.Any, typing.Any]:
        return {'broadcast_db_worker': self.dp['broadcast_db_worker']}

    async def on_pre_process_message(self, message: types.Message, data: typing.Dict[typing.Any, typing.Any]):
        data.update(self.db_data())
    
    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: typing.Dict[typing.Any, typing.Any]):
        data.update(self.db_data())
