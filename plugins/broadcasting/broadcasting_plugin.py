from config import config
import typing

from aiogram import Dispatcher
from loguru import logger
from datetime import datetime
from aiogram_plugin import WhenToCall

from loguru import logger

from aiogram_plugin import AiogramPlugin

from .handlers.broadcast_handlers import BroadcastHandlers
from .middlewares.DBmiddleware import AddBroadcastDBMiddleware
from .controllers.db_controller import create_db
from .controllers.rmq_controller import RabbitMQ
from .controllers.monitor_controller import create_event_monitor
from .broadcast_system_config import config
from datetime import datetime
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def connect_to_db(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any] = {}):
    logger.info(config)
    dp['broadcast_db_worker'] = await create_db(**config['db_broadcast_settings'])
    rmq = RabbitMQ(**config['rmq_settings'])
    await rmq.connect()
    dp['event_monitor'] = create_event_monitor(dp['broadcast_db_worker'], rmq, config)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(dp['event_monitor'].check_events, 'interval', seconds=config['sleep_time'])
    scheduler.start()


broadcating_plugin = AiogramPlugin('Broadcasting', config = config)
broadcating_plugin.plug_handler(BroadcastHandlers)
broadcating_plugin.plug_middleware(AddBroadcastDBMiddleware)
broadcating_plugin.plug_custom_method(connect_to_db)