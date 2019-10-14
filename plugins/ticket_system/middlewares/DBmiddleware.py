import typing

from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware


class AddTicketDBMiddleware(BaseMiddleware):
    def __init__(self, dp: Dispatcher):
        self.dp: Dispatcher = dp
        super(AddTicketDBMiddleware, self).__init__()

    def db_data(self) -> typing.Dict[typing.Any, typing.Any]:
        return {'ticket_db_worker': self.dp['ticket_db_worker']}

    async def on_pre_process_message(self, message: types.Message, data: typing.Dict[typing.Any, typing.Any]):
        data.update(self.db_data())
    
    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: typing.Dict[typing.Any, typing.Any]):
        data.update(self.db_data())
