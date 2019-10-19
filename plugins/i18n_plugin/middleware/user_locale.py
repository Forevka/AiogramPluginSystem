from plugins.i18n_plugin.controllers.db_controller import I18nDBworker
from plugins.i18n_plugin.controllers.i18n_controller import LocaleController
from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware

from loguru import logger
from ..i18n_config import config

class GetUserLocale(BaseMiddleware):
    def __init__(self, dp: Dispatcher):
        self.i18n_controller: LocaleController = dp['locale_controller']
        self.db: I18nDBworker = dp['i18n_db']
        super(GetUserLocale, self).__init__()

    async def get_data(self, user_id: int):
        data = {}
        user = await self.db.create_or_find_user(user_id)
        data['i18n_controller'] = self.i18n_controller
        data['i18n_dbworker'] = self.db
        if user:
            data['_'] = self.i18n_controller.get_locale(user.lang)
        else:
            data['_'] = self.i18n_controller.get_locale(config['default_lang'])
        
        return data

    async def on_pre_process_message(self, message: types.Message, data: dict):
        data.update(await self.get_data(message.from_user.id))
        
    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        data.update(await self.get_data(callback_query.from_user.id))