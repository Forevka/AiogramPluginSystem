import typing

from aiogram import Bot, Dispatcher, executor, types
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from loguru import logger

from aiogram_plugin import AiogramHandlerPack

from ..controllers.db_controller import TicketDBworker
from ..filters.IsReplyToBot import IsReplyToBot
from ..models.ticket import TicketStatus
from ..models.ticket import Ticket


# State
class TicketForm(StatesGroup):
    get_text = State()  # Will be represented in storage as 'TicketForm:get_text'
    get_reply = State()


ticket_cb = CallbackData('ticket', 'id', 'action')
conversation_cb = CallbackData(
    'conversation', 'ticket_id', 'action', 'conv_id')
change_status_cb = CallbackData('ticket_status', 'id', 'new_status')


def generate_ticket_kb(ticket: Ticket,) -> types.InlineKeyboardMarkup:
    kb_action = types.InlineKeyboardMarkup()
    kb_action.row(
        types.InlineKeyboardButton(
            "Reply 📤", callback_data=ticket_cb.new(id=str(ticket.ticket_id), action='reply')),
        types.InlineKeyboardButton(
            "Change status", callback_data=ticket_cb.new(id=str(ticket.ticket_id), action='change_status')),
    )
    kb_action.row(
        types.InlineKeyboardButton(
            "⬅️ Back to list", callback_data=ticket_cb.new(id=1, action='next_page')),
        types.InlineKeyboardButton(
            "See all conversations 📃", callback_data=conversation_cb.new(ticket_id=str(ticket.ticket_id), action='show', conv_id='0')),
    )

    return kb_action


def ticket_desccription(ticket: Ticket, additional_text: str = '',):
    is_from = (
        '<b>support</b>' if ticket.conversations[0].is_from_support else '<b>user</b>')

    return additional_text + ('\nTicket id {}\n\nFrom <a href="tg://user?id={}">User</a>\nLast conversation from {}: {}\n\nCreated at: {}\nStatus: {}').format(ticket.ticket_id, ticket.user_id, is_from, ticket.conversations[0].text, ticket.created_at.strftime("%m/%d/%Y, %H:%M:%S"), str(ticket.status.name.lower().title().replace('_', ' ')))


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
            TicketHandlers.query_show_ticket_conversation, conversation_cb.filter(action='show'))

        dp.register_callback_query_handler(
            TicketHandlers.query_change_status_new_ticket, change_status_cb.filter())

        dp.register_message_handler(TicketHandlers.echo)

        return True

    @staticmethod
    async def create_ticket(message: types.Message):
        await TicketForm.get_text.set()

        await message.answer("Please type you question")

    @staticmethod
    async def query_change_status_new_ticket(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: TicketDBworker, ticket_support_config: typing.Dict, bot: Bot):
        await ticket_db_worker.update_ticket_status(callback_data['id'], TicketStatus(int(callback_data['new_status'])))
        ticket = await ticket_db_worker.find_ticket(callback_data['id'])
        if ticket:
            kb_action = generate_ticket_kb(ticket)

            await query.message.edit_text(ticket_desccription(ticket, additional_text='<b>Status changed.</b>',), reply_markup=kb_action, parse_mode='HTML')

    @staticmethod
    async def query_change_status_ticket(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: TicketDBworker, ticket_support_config: typing.Dict, bot: Bot):
        ticket = await ticket_db_worker.find_ticket(callback_data['id'])
        if ticket:
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

            await query.message.edit_text(ticket_desccription(ticket, additional_text='<b>Choose new status for</b>',), reply_markup=kb_statuses, parse_mode='HTML')

    @staticmethod
    async def process_question_reply(message: types.Message, state: FSMContext, ticket_db_worker: TicketDBworker, bot: Bot, ticket_support_config: typing.Dict):
        ticket = None
        async with state.proxy() as data:
            reply_to_user_msg = await bot.send_message(data['user_id'], "Support answer to you question:\n" + message.text + "\n\nYou can reply to support by replying this message!", reply_to_message_id=data['user_message_id'])
            await ticket_db_worker.update_ticket_status(data['ticket_id'], TicketStatus.ON_REVIEW)
            await ticket_db_worker.add_conversation(message.text, data['ticket_id'], message.from_user.id, True, message.message_id, reply_to_user_msg.message_id)
            ticket = await ticket_db_worker.find_ticket(str(data['ticket_id']))
        if ticket:
            kb_action = generate_ticket_kb(ticket)

            await message.answer(ticket_desccription(ticket, additional_text='<b>Answered and changed status to On review</b>',), reply_markup=kb_action, parse_mode='HTML')
            await state.finish()

    @staticmethod
    async def process_new_ticket_reply(message: types.Message, state: FSMContext, ticket_db_worker: TicketDBworker, bot: Bot, ticket_support_config: typing.Dict):
        ticket = await ticket_db_worker.find_ticket_by_message_reply_id(message.from_user.id, message.reply_to_message.message_id)
        if ticket:
            await ticket_db_worker.add_conversation(message.text, ticket.ticket_id, message.from_user.id, False, message.message_id, message.reply_to_message.message_id)
            await message.reply("Ok I will send this question to support!\nWait for answer, i notify. Thank you")

    @staticmethod
    async def process_question_text(message: types.Message, state: FSMContext, ticket_db_worker: TicketDBworker, bot: Bot, ticket_support_config: typing.Dict):
        await ticket_db_worker.create_ticket(message.from_user.id, message.text, message.message_id)
        await bot.send_message(ticket_support_config['GROUP_LINK'], message.text)
        await message.reply("Ok I will send this question to support!\nWait for answer, i notify. Thank you")
        await state.finish()

    @staticmethod
    async def cmd_get_tickets(message: types.Message, ticket_db_worker: TicketDBworker, ticket_support_config: typing.Dict):
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
    async def query_show_ticket(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: TicketDBworker, ticket_support_config: typing.Dict, bot: Bot):
        ticket = await ticket_db_worker.find_ticket(callback_data['id'])
        if ticket:
            kb_action = generate_ticket_kb(ticket)

            await query.message.edit_text(ticket_desccription(ticket), reply_markup=kb_action, parse_mode='HTML')

    @staticmethod
    async def query_show_ticket_conversation(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: TicketDBworker, ticket_support_config: typing.Dict, bot: Bot, state: FSMContext):
        ticket = await ticket_db_worker.find_ticket(callback_data['ticket_id'])
        this_conversation = ticket.conversations[int(callback_data['conv_id'])]
        kb_action = types.InlineKeyboardMarkup()
        l = []

        if int(callback_data['conv_id']) > 0:
            l.append(
                types.InlineKeyboardButton(
                    "⬅️ Newest", callback_data=conversation_cb.new(ticket_id=str(ticket.ticket_id), action='show', conv_id=int(callback_data['conv_id']) - 1)),
            )

        if int(callback_data['conv_id']) < len(ticket.conversations) - 1:
            l.append(
                types.InlineKeyboardButton(
                    "Older ➡️", callback_data=conversation_cb.new(ticket_id=str(ticket.ticket_id), action='show', conv_id=int(callback_data['conv_id']) + 1)),
            )

        kb_action.row(*l)
        kb_action.add(
            types.InlineKeyboardButton(
                "Back to ticket", callback_data=ticket_cb.new(id=ticket.ticket_id, action='show')),
        )

        await query.message.edit_text(('Ticket id {}\n\nFrom <a href="tg://user?id={}">User</a>\nConversation #️⃣ {} from ' + ('<b>support</b>' if this_conversation.is_from_support else '<b>user</b>') + ' : {}\n\nCreated at: {}\nStatus: {}').format(ticket.ticket_id, ticket.user_id, len(ticket.conversations) - int(callback_data['conv_id']), this_conversation.text, this_conversation.created_at.strftime("%m/%d/%Y, %H:%M:%S"), str(ticket.status.name.lower().title().replace('_', ' '))), reply_markup=kb_action, parse_mode='HTML')

    @staticmethod
    async def query_reply_to_ticket(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: TicketDBworker, ticket_support_config: typing.Dict, bot: Bot, state: FSMContext):
        ticket = await ticket_db_worker.find_ticket(callback_data['id'])
        await TicketForm.get_reply.set()
        async with state.proxy() as data:
            data['ticket_id'] = str(ticket.ticket_id)
            data['user_id'] = str(ticket.user_id)
            data['user_message_id'] = str(ticket.conversations[0].message_id)

        await query.message.edit_text("Please type you reply to ticket.\n\nLast conversation: {}".format(ticket.conversations[0].text))

    @staticmethod
    async def query_get_tickets(query: types.CallbackQuery, callback_data: dict, ticket_db_worker: TicketDBworker, ticket_support_config: typing.Dict):
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
    async def echo(message: types.Message, _plugin_name: typing.Any, ticket_support_config: dict):
        print(_plugin_name)
        print(ticket_support_config)
        await message.answer(message.text)
