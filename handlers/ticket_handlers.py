from aiogram import Bot, Dispatcher, executor, types
from controllers.db_controller import DBworker
import typing

from loguru import logger

from aiogram import Bot, Dispatcher, types

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram_plugins import AiogramHandlerPack

# States
class TicketForm(StatesGroup):
    get_text = State()  # Will be represented in storage as 'TicketForm:get_text'


class TicketHandlers(AiogramHandlerPack):
    @staticmethod
    def register(dp: Dispatcher) -> bool:
        dp.register_message_handler(
            TicketHandlers.create_ticket, commands=['ticket'])
        dp.register_message_handler(
            TicketHandlers.process_question_text, state=TicketForm.get_text)
        dp.register_message_handler(TicketHandlers.echo)

        return True

    @staticmethod
    async def create_ticket(message: types.Message):
        await TicketForm.get_text.set()

        await message.answer("Please type you question")

    @staticmethod
    async def process_question_text(message: types.Message, state: FSMContext, ticket_db_worker: DBworker):
        await ticket_db_worker.create_ticket(message.from_user.id, message.text)

        await state.finish()
        await message.reply("Ok I will send this question to support!\nWait for answer, i notify. Thank you")

    @staticmethod
    async def echo(message: types.Message):
        await message.answer(message.text)
