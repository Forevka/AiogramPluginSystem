from datetime import date, datetime
from plugins.broadcasting.controllers.db_controller import BroadcastingDBworker
import typing

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from loguru import logger

from aiogram_plugin import AiogramHandlerPack
from uuid import UUID

from ..calendar_keyboard import calendar_cb, generate_calendar, generate_time_kb, generate_event_kb
from ..models.event import Event

# State
class CalendarForm(StatesGroup):
    get_text = State()


class BroadcastHandlers(AiogramHandlerPack):
    @staticmethod
    def register(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any]) -> bool:
        dp.register_message_handler(
            BroadcastHandlers.cmd_calendar, commands=['calendar'])

        dp.register_callback_query_handler(
            BroadcastHandlers.query_change_calendar, calendar_cb.filter(action='change'))

        dp.register_callback_query_handler(
            BroadcastHandlers.query_day, calendar_cb.filter(action='select_day'))

        dp.register_callback_query_handler(
            BroadcastHandlers.query_new_event, calendar_cb.filter(action='new_event'))
        
        dp.register_callback_query_handler(
            BroadcastHandlers.query_time, calendar_cb.filter(action='select_time'))

        dp.register_message_handler(
            BroadcastHandlers.process_question_reply, state=CalendarForm.get_text)

        return True

    @staticmethod
    async def cmd_calendar(message: types.Message):
        now: datetime = datetime.now()
        calendar_kb = generate_calendar(now.year, now.month)
        await message.answer(f'Choose day from keyboard\nYear: {now.year}\nMonth: {now.month}', reply_markup=calendar_kb)
    
    @staticmethod
    async def process_question_reply(message: types.Message, state: FSMContext, broadcast_db_worker: BroadcastingDBworker):
        async with state.proxy() as data:
            this_date = datetime(int(data['year']), 
                                int(data['month']), 
                                int(data['day']),
                                int(data['time']))
            
            event_id: UUID = await broadcast_db_worker.create_event(this_date, message.text, message.from_user.id)
            actions_kb = generate_event_kb(event_id, this_date)

            await message.answer("New event for {}\nWith text: {}".format(this_date.strftime('%Y-%m-%d %H:%M'), message.text), reply_markup=actions_kb)
        
        await state.finish()

    @staticmethod
    async def query_change_calendar(query: types.CallbackQuery, callback_data: dict):
        calendar_kb = generate_calendar(
            int(callback_data['year']), int(callback_data['month']))
        await query.message.edit_text(f"Choose day from keyboard\nYear: {callback_data['year']}\nMonth: {callback_data['month']}", reply_markup=calendar_kb)

    @staticmethod
    async def query_day(query: types.CallbackQuery, callback_data: dict):
        logger.info(callback_data)

        events = []

        this_date = date(int(callback_data['year']), int(
            callback_data['month']), int(callback_data['day']))
        actions_kb = InlineKeyboardMarkup()
        actions_kb.row(
            InlineKeyboardButton('Add new event', callback_data=calendar_cb.new(
                time='00', day=callback_data['day'], month=callback_data['month'], year=callback_data['year'], action="new_event")),
            InlineKeyboardButton('Back to calendar', callback_data=calendar_cb.new(
                time='00', day=callback_data['day'], month=callback_data['month'], year=callback_data['year'], action="change")),
        )

        await query.message.edit_text("Events for {}\n\n{}".format(this_date.strftime('%Y-%m-%d'), 1), reply_markup=actions_kb)

    @staticmethod
    async def query_new_event(query: types.CallbackQuery, callback_data: dict):
        kb = generate_time_kb(int(callback_data['year']), 
                                int(callback_data['month']), 
                                int(callback_data['day']),)
        kb.row(InlineKeyboardButton('Back to event list', callback_data=calendar_cb.new(
                                                                            time='00', 
                                                                            day=callback_data['day'], 
                                                                            month=callback_data['month'], 
                                                                            year=callback_data['year'], 
                                                                            action="select_day")))

        await query.message.edit_text("Pick time", reply_markup=kb)
    
    @staticmethod
    async def query_time(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
        await CalendarForm.get_text.set()
        async with state.proxy() as data:
            data['time'] = callback_data['time']
            data['day'] = callback_data['day']
            data['month'] = callback_data['month']
            data['year'] = callback_data['year']
        await query.message.edit_text("Type text for broadcast", reply_markup=InlineKeyboardMarkup())
