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

from ..calendar_keyboard import calendar_cb, event_cb, generate_calendar, generate_time_kb, generate_event_kb
from ..models.event import Event

# State
class CalendarForm(StatesGroup):
    get_text = State()
    edit_text = State()
    edit_event_time = State()


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
        
        dp.register_callback_query_handler(
            BroadcastHandlers.query_show_event, event_cb.filter(action='show'))
        
        dp.register_callback_query_handler(
            BroadcastHandlers.query_delete_event, event_cb.filter(action='delete'))
        
        dp.register_callback_query_handler(
            BroadcastHandlers.query_yes_delete_event, event_cb.filter(action='yes_delete'))

        dp.register_callback_query_handler(
            BroadcastHandlers.query_edit_text_event, event_cb.filter(action='edit'))

        dp.register_message_handler(
            BroadcastHandlers.process_question_reply, state=CalendarForm.get_text)
        
        dp.register_message_handler(
            BroadcastHandlers.process_edit_text_reply, state=CalendarForm.edit_text)

        return True

    @staticmethod
    async def cmd_calendar(message: types.Message, broadcast_db_worker: BroadcastingDBworker):
        now: datetime = datetime.now()
        events = await broadcast_db_worker.find_events_for_month(datetime(int(now.year), 
                                                                            int(now.month), 
                                                                            int(now.day)))
        calendar_kb = generate_calendar(now.year, now.month, events)
        await message.answer(f'Choose day from keyboard\nYear: {now.year}\nMonth: {now.month}', reply_markup=calendar_kb)
    
    @staticmethod
    async def query_yes_delete_event(query: types.CallbackQuery, callback_data: dict, broadcast_db_worker: BroadcastingDBworker):
        await broadcast_db_worker.delete_event_by_id(callback_data['event_id'])

        now: datetime = datetime.now()
        events = await broadcast_db_worker.find_events_for_month(datetime(int(now.year), 
                                                                            int(now.month), 
                                                                            int(now.day)))
        calendar_kb = generate_calendar(now.year, now.month, events)

        await query.message.edit_text("*Event deleted.*\n\n"+f'Choose day from keyboard\nYear: {now.year}\nMonth: {now.month}', reply_markup=calendar_kb)

    @staticmethod
    async def query_delete_event(query: types.CallbackQuery, callback_data: dict):
        kb = InlineKeyboardMarkup()
        kb.row(
            InlineKeyboardButton("Yes, delete this shhh", callback_data=event_cb.new(event_id = callback_data['event_id'], action = "yes_delete")),
            InlineKeyboardButton("No, i change my mind", callback_data=event_cb.new(event_id = callback_data['event_id'], action = "show")),
        )
        await query.message.edit_text("Do you really wanna delete this event?", reply_markup=kb)

    @staticmethod
    async def query_show_event(query: types.CallbackQuery, callback_data: dict, broadcast_db_worker: BroadcastingDBworker):
        event_id: UUID = callback_data['event_id']
        event = await broadcast_db_worker.find_event_by_id(event_id)
        actions_kb = generate_event_kb(event_id, event.when_execute)
        if event:
            await query.message.edit_text("Event for {}\nWith text: {}".format(event.when_execute.strftime('%Y-%m-%d %H:%M'), event.text), reply_markup=actions_kb)

    @staticmethod
    async def query_edit_text_event(query: types.CallbackQuery, state: FSMContext, callback_data: dict, broadcast_db_worker: BroadcastingDBworker):
        await CalendarForm.edit_text.set()
        async with state.proxy() as data:
            data['event_id'] = callback_data['event_id']
        
        event = await broadcast_db_worker.find_event_by_id(callback_data['event_id'])

        await query.message.edit_text("Type new text for this event\nOld text: {}".format(event.text), reply_markup=InlineKeyboardMarkup())

    @staticmethod
    async def process_edit_text_reply(message: types.Message, state: FSMContext, broadcast_db_worker: BroadcastingDBworker):
        async with state.proxy() as data:
            event = await broadcast_db_worker.update_text_in_event(data['event_id'], message.text, message.from_user.id)
            if event:
                actions_kb = generate_event_kb(data['event_id'], event.when_execute)
                await message.answer("*Message text updated*\n\n"+"Event for {}\nWith text: {}".format(event.when_execute.strftime('%Y-%m-%d %H:%M'), event.text), reply_markup=actions_kb)
        
        await state.finish()



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
    async def query_change_calendar(query: types.CallbackQuery, callback_data: dict, broadcast_db_worker: BroadcastingDBworker):
        events = await broadcast_db_worker.find_events_for_month(datetime(int(callback_data['year']), 
                                                                            int(callback_data['month']), 
                                                                            int(callback_data['day']),
                                                                            int(callback_data['time'])))
        calendar_kb = generate_calendar(
            int(callback_data['year']), int(callback_data['month']), events)
        await query.message.edit_text(f"Choose day from keyboard\nYear: {callback_data['year']}\nMonth: {callback_data['month']}", reply_markup=calendar_kb)

    @staticmethod
    async def query_day(query: types.CallbackQuery, callback_data: dict, broadcast_db_worker: BroadcastingDBworker):
        logger.info(callback_data)
        this_date = date(int(callback_data['year']), 
                            int(callback_data['month']), 
                            int(callback_data['day']))

        show_next_button, events = await broadcast_db_worker.find_event_for_day(this_date)
        '''l = []
        if show_next_button:
            l.append(
                types.InlineKeyboardButton(
                    "Next ➡️", callback_data=ticket_cb.new(id=cur_page + 1, action='next_page')),
            )'''

        actions_kb = InlineKeyboardMarkup()
        for event in events:
            actions_kb.add(InlineKeyboardButton('Event for {:02d}:00'.format(event.when_execute.hour), callback_data=event_cb.new(event_id=str(event.event_id), action='show')))

        actions_kb.row(
            InlineKeyboardButton('Add new event', callback_data=calendar_cb.new(
                time='00', day=callback_data['day'], month=callback_data['month'], year=callback_data['year'], action="new_event")),
            InlineKeyboardButton('Back to calendar', callback_data=calendar_cb.new(
                time='00', day=callback_data['day'], month=callback_data['month'], year=callback_data['year'], action="change")),
        )

        await query.message.edit_text("Events for {}".format(this_date.strftime('%Y-%m-%d')), reply_markup=actions_kb)

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
