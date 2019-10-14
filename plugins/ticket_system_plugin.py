from aiogram import Dispatcher
from loguru import logger

from aiogram_plugins import AiogramPlugin
import config
from controllers.db_controller import create_db
from handlers.ticket_handlers import TicketHandlers
from middlewares.DBmiddleware import AddTicketDBMiddleware

async def connect_to_db(dp: Dispatcher):
    dp['ticket_db_worker'] = await create_db(**config.db_ticket_settings)

ticket_plugin = AiogramPlugin('TicketSupportSystem')
ticket_plugin.plug_middleware(AddTicketDBMiddleware)
ticket_plugin.plug_handler(TicketHandlers)
ticket_plugin.plug_custom_method(connect_to_db)