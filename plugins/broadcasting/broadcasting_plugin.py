from datetime import datetime
from aiogram_plugin import WhenToCall

from loguru import logger

from aiogram_plugin import AiogramPlugin

from .handlers.broadcast_handlers import BroadcastHandlers



broadcating_plugin = AiogramPlugin('Broadcasting')
broadcating_plugin.plug_handler(BroadcastHandlers)