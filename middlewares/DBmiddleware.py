import logging
import time
import typing

from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware

from controllers.db_controller import DBworker


class AddTicketDBMiddleware(BaseMiddleware):
    def __init__(self, dp: Dispatcher):
        self.dp: Dispatcher = dp
        super(AddTicketDBMiddleware, self).__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict):
        data['ticket_db_worker'] = self.dp['ticket_db_worker']
