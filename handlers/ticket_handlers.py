from models.ticket import TicketStatus
from aiogram import Bot, Dispatcher, executor, types
from controllers.db_controller import DBworker
import config
import typing

from loguru import logger

from aiogram import Bot, Dispatcher, types

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

from aiogram_plugins import AiogramHandlerPack
from filters.IsReplyToBot import IsReplyToBot

from models.ticket import Ticket

# States


class TicketForm(StatesGroup):
    get_text = State()  # Will be represented in storage as 'TicketForm:get_text'
    get_reply = State()


ticket_cb = CallbackData('ticket', 'id', 'action')
change_status_cb = CallbackData('ticket_status', 'id', 'new_status')


class TicketHandlers(AiogramHandlerPack):
    @staticmethod
    def register(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any]) -> bool:
        dp.register_message_handler(
            TicketHandlers.create_ticket, commands=['ticket'])
        dp.register_message_handler(
            TicketHandlers.process_question_text, state=TicketForm.get_text)
        dp.register_message_handler(
            TicketHandlers.process_question_reply, state=TicketForm.get_reply)

        dp.register_message_handler(
            TicketHandlers.process_new_ticket_reply, IsReplyToBot())

        dp.register_message_handler(
            TicketHandlers.cmd_get_tickets, commands=['ticket_list'])

        dp.register_callback_query_handler(
            TicketHandlers.query_get_tickets, ticket_cb.filter(action='next_page'))

        dp.register_callback_query_handler(
            TicketHandlers.query_show_ticket, ticket_cb.filter(action='show'))

        dp.register_callback_query_handler(
            TicketHandlers.query_reply_to_ticket, ticket_cb.filter(action='reply'))

        dp.register_callback_query_handler(
            TicketHandlers.query_change_status_ticket, ticket_cb.filter(action='change_status'))

        dp.register_callback_query_handler(
            TicketHandlers.query_change_status_new_ticket, change_status_cb.filter())
            

        dp.register_message_handler(TicketHandlers.echo)

        return True

    @staticmethod
    async def create_ticket(message: types.Message):
        await TicketForm.get_text.set()

        await message.answer("Please type you question")

    @staticmethod
    async def query_change_status_new_ticket(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: DBworker, ticket_support_config: typing.Dict, bot: Bot):
        await ticket_db_worker.update_ticket_status(callback_data['id'], TicketStatus(int(callback_data['new_status'])))
        ticket = await ticket_db_worker.find_ticket(callback_data['id'])

        kb_action = types.InlineKeyboardMarkup()
        kb_action.row(
            types.InlineKeyboardButton(
                "Reply 📤", callback_data=ticket_cb.new(id=str(ticket.ticket_id), action='reply')),
            types.InlineKeyboardButton(
                "Change status", callback_data=ticket_cb.new(id=str(ticket.ticket_id), action='change_status')),
        )

        await query.message.edit_text('<b>Status changed.</b>\nTicket id {}\n\nFrom <a href="tg://user?id={}">User</a>\nLast conversation: {}\n\nCreated at: {}\nStatus: {}'.format(ticket.ticket_id, ticket.user_id, ticket.conversations[-1].text, ticket.created_at.strftime("%m/%d/%Y, %H:%M:%S"), str(ticket.status.name.lower().title().replace('_', ' '))), reply_markup=kb_action, parse_mode='HTML')

    @staticmethod
    async def query_change_status_ticket(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: DBworker, ticket_support_config: typing.Dict, bot: Bot):
        ticket = await ticket_db_worker.find_ticket(callback_data['id'])
        kb_statuses = types.InlineKeyboardMarkup()
        for s in TicketStatus:
            if s.value != ticket.status.value:
                kb_statuses.add(
                    types.InlineKeyboardButton(
                        "Status: " + s.name.lower().title().replace('_', ' '), callback_data=change_status_cb.new(id=str(ticket.ticket_id), new_status=str(s.value))),
                )

        kb_statuses.add(
            types.InlineKeyboardButton(
                "⬅️ Back", callback_data=ticket_cb.new(id=ticket.ticket_id, action='show')),
        )

        await query.message.edit_text('<b>Changing status for </b>\nTicket id {}\n\nFrom <a href="tg://user?id={}">User</a>\nLast conversation: {}\n\nCreated at: {}\nStatus: {}'.format(ticket.ticket_id, ticket.user_id, ticket.conversations[-1].text, ticket.created_at.strftime("%m/%d/%Y, %H:%M:%S"), str(ticket.status.name.lower().title().replace('_', ' '))), reply_markup=kb_statuses, parse_mode='HTML')

    @staticmethod
    async def process_question_reply(message: types.Message, state: FSMContext, ticket_db_worker: DBworker, bot: Bot, ticket_support_config: typing.Dict):
        ticket = None
        async with state.proxy() as data:
            await bot.send_message(data['user_id'], "Support answer to you question:\n" + message.text + "\n\nYou can reply to support by replying this message!", reply_to_message_id=data['user_message_id'])
            await ticket_db_worker.update_ticket_status(data['ticket_id'], TicketStatus.ON_REVIEW)
            ticket = await ticket_db_worker.find_ticket(str(data['ticket_id']))

        await state.finish()
        kb_action = types.InlineKeyboardMarkup()
        kb_action.row(
            types.InlineKeyboardButton(
                "Reply 📤", callback_data=ticket_cb.new(id=str(ticket.ticket_id), action='reply')),
            types.InlineKeyboardButton(
                "Change status", callback_data=ticket_cb.new(id=str(ticket.ticket_id), action='change_status')),
        )

        await message.answer('<b>Answered and changed status to On review</b>\nTicket id {}\n\nFrom <a href="tg://user?id={}">User</a>\nLast conversation: {}\n\nCreated at: {}\nStatus: {}'.format(ticket.ticket_id, ticket.user_id, ticket.conversations[-1].text, ticket.created_at.strftime("%m/%d/%Y, %H:%M:%S"), str(ticket.status.name.lower().title().replace('_', ' '))), reply_markup=kb_action, parse_mode='HTML')


    @staticmethod
    async def process_new_ticket_reply(message: types.Message, state: FSMContext, ticket_db_worker: DBworker, bot: Bot, ticket_support_config: typing.Dict):
        pass


    @staticmethod
    async def process_question_text(message: types.Message, state: FSMContext, ticket_db_worker: DBworker, bot: Bot, ticket_support_config: typing.Dict):
        await ticket_db_worker.create_ticket(message.from_user.id, message.text, message.message_id)
        await state.finish()
        await bot.send_message(ticket_support_config['GROUP_LINK'], message.text)
        await message.reply("Ok I will send this question to support!\nWait for answer, i notify. Thank you")

    @staticmethod
    async def cmd_get_tickets(message: types.Message, ticket_db_worker: DBworker, ticket_support_config: typing.Dict):
        show_next_button, tickets = await ticket_db_worker.find_tickets(page=1, per_page=ticket_support_config['ticket_per_page'])
        kb = types.InlineKeyboardMarkup()
        for i in tickets:
            kb.add(
                types.InlineKeyboardButton(
                    "From user: " + str(i.user_id) + " status " + str(i.status.name.lower().title()), callback_data=ticket_cb.new(id=i.ticket_id, action='show')),
            )

        if show_next_button:
            kb.add(
                types.InlineKeyboardButton(
                    "Show older ➡️", callback_data=ticket_cb.new(id='2', action='next_page')),
            )

        await message.answer("Ticket list page 1", reply_markup=kb)

    @staticmethod
    async def query_show_ticket(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: DBworker, ticket_support_config: typing.Dict, bot: Bot):
        ticket: Ticket = await ticket_db_worker.find_ticket(callback_data['id'])
        logger.info(ticket)
        for i in ticket.conversations:
            logger.info(i)
        
        kb_action = types.InlineKeyboardMarkup()
        kb_action.row(
            types.InlineKeyboardButton(
                "Reply 📤", callback_data=ticket_cb.new(id=str(ticket.ticket_id), action='reply')),
            types.InlineKeyboardButton(
                "Change status", callback_data=ticket_cb.new(id=str(ticket.ticket_id), action='change_status')),
        )

        await query.message.edit_text('Ticket id {}\n\nFrom <a href="tg://user?id={}">User</a>\nLast conversation: {}\n\nCreated at: {}\nStatus: {}'.format(ticket.ticket_id, ticket.user_id, ticket.conversations[-1].text, ticket.created_at.strftime("%m/%d/%Y, %H:%M:%S"), str(ticket.status.name.lower().title().replace('_', ' '))), reply_markup=kb_action, parse_mode='HTML')

    @staticmethod
    async def query_reply_to_ticket(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: DBworker, ticket_support_config: typing.Dict, bot: Bot, state: FSMContext):
        ticket = await ticket_db_worker.find_ticket(callback_data['id'])
        await TicketForm.get_reply.set()
        async with state.proxy() as data:
            data['ticket_id'] = str(ticket.ticket_id)
            data['user_id'] = str(ticket.user_id)
            data['user_message_id'] = str(ticket.user_message_id)

        await query.message.edit_text("Please type you reply to ticket.\n\nLast conversation: {}".format(ticket.conversations[-1].text))

    @staticmethod
    async def query_get_tickets(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: DBworker, ticket_support_config: typing.Dict):
        page = int(callback_data['id'])
        show_next_button, tickets = await ticket_db_worker.find_tickets(page=page, per_page=ticket_support_config['ticket_per_page'])
        kb = types.InlineKeyboardMarkup()
        for i in tickets:
            kb.add(
                types.InlineKeyboardButton(
                    "From user: " + str(i.user_id) + " status " + str(i.status.name.lower().title()), callback_data=ticket_cb.new(id=i.ticket_id, action='show')),
            )

        l = []
        if page > 1:
            l.append(
                types.InlineKeyboardButton(
                    "⬅️ Show newest", callback_data=ticket_cb.new(id=page - 1, action='next_page')),
            )

        if show_next_button:
            l.append(
                types.InlineKeyboardButton(
                    "Show older ➡️", callback_data=ticket_cb.new(id=page + 1, action='next_page')),
            )

        kb.row(*l)

        await query.message.edit_text("Ticket list page {}".format(page), reply_markup=kb)

    @staticmethod
    async def echo(message: types.Message):
        await message.answer(message.text)
