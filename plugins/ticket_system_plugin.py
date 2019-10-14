import typing

from aiogram import Dispatcher
from loguru import logger

from aiogram_plugins import AiogramPlugin
from controllers.db_controller import create_db
from handlers.ticket_handlers import TicketHandlers
from middlewares.BotContextMiddleware import BotContextMiddleware
from middlewares.DBmiddleware import AddTicketDBMiddleware

from plugins import ticket_system_config

async def connect_to_db(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any] = {}):
    logger.info(config)
    dp['ticket_db_worker'] = await create_db(**config['db_ticket_settings'])

ticket_plugin = AiogramPlugin('TicketSupport', ticket_system_config.config)

ticket_plugin.plug_middleware(AddTicketDBMiddleware)
ticket_plugin.plug_middleware(BotContextMiddleware)

ticket_plugin.plug_handler(TicketHandlers)

ticket_plugin.plug_custom_method(connect_to_db)