from datetime import datetime
import typing

from aiogram import Dispatcher, types, Bot
from loguru import logger

from aiogram_plugin import AiogramHandlerPack
from ..calendar_keyboard import generate_calendar, calendar_cb

class BroadcastHandlers(AiogramHandlerPack):
    """
        you can simple create you own class
        with your own handlers
    """
    @staticmethod
    def register(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any]) -> bool:
        dp.register_message_handler(BroadcastHandlers.cmd_calendar, commands=['calendar'])

        dp.register_callback_query_handler(
            BroadcastHandlers.query_change_calendar, calendar_cb.filter(action='change'))
        
        dp.register_callback_query_handler(
            BroadcastHandlers.query_day, calendar_cb.filter(action='select_day'))

        return True
    
    @staticmethod
    async def cmd_calendar(message: types.Message):
        now: datetime = datetime.now()
        calendar_kb = generate_calendar(now.year, now.month)
        await message.answer(f'Choose day from keyboard\nYear: {now.year}\nMonth: {now.month}', reply_markup=calendar_kb)
    
    @staticmethod
    async def query_change_calendar(query: types.CallbackQuery, callback_data: dict):
        calendar_kb = generate_calendar(int(callback_data['year']), int(callback_data['month']))
        await query.message.edit_text(f"Choose day from keyboard\nYear: {callback_data['year']}\nMonth: {callback_data['month']}", reply_markup=calendar_kb)
    
    @staticmethod
    async def query_day(query: types.CallbackQuery, callback_data: dict):
       pass 