from typing import Union

from aiogram.dispatcher.filters.filters import Filter
from aiogram.types import CallbackQuery, Message, Chat, User

#LOGGING
from loguru import logger
from aiogram import Bot, Dispatcher


class IsReplyToBot(Filter):
    async def check(self, obj: Union[Message, CallbackQuery]):
        if getattr(obj, "reply_to_message"):
            logger.info(obj.reply_to_message.from_user.id)
            if Chat.get_current().id == User.get_current().id:
                return True
        
        return False