from datetime import datetime, date
import typing

from aiogram import Dispatcher, types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from aiogram_plugin import AiogramHandlerPack
from ..calendar_keyboard import generate_calendar, calendar_cb
from aiogram.utils.callback_data import CallbackData

# State
class CalendarForm(StatesGroup):
    get_text = State()  

class BroadcastHandlers(AiogramHandlerPack):
    @staticmethod
    def register(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any]) -> bool:
        dp.register_message_handler(BroadcastHandlers.cmd_calendar, commands=['calendar'])

        dp.register_callback_query_handler(
            BroadcastHandlers.query_change_calendar, calendar_cb.filter(action='change'))
        
        dp.register_callback_query_handler(
            BroadcastHandlers.query_day, calendar_cb.filter(action='select_day'))

        dp.register_callback_query_handler(
            BroadcastHandlers.query_new_event, calendar_cb.filter(action='new_event'))
        
        #dp.register_message_handler(
        #    BroadcastHandlers.process_question_reply, state=CalendarForm.get_text)

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
       events = []
       logger.info(callback_data)
       this_date = date(int(callback_data['year']), int(callback_data['month']), int(callback_data['day']))
       actions_kb = InlineKeyboardMarkup()
       actions_kb.row(InlineKeyboardButton('Add new event', callback_data=calendar_cb.new(day = callback_data['day'], month=callback_data['month'], year=callback_data['year'], action = "new_event")))


       await query.message.edit_text("Events for {}".format(this_date.strftime('%Y-%m-%d')), reply_markup=actions_kb)
    
    @staticmethod
    async def query_new_event(query: types.CallbackQuery, callback_data: dict):
        await CalendarForm.get_text.set()

        await query.message.answer("Please type text for broadcast him")