import typing

from aiogram import Bot, Dispatcher, types
from aiogram.utils.callback_data import CallbackData
from loguru import logger

from aiogram_plugin import AiogramHandlerPack

from ..controllers.db_controller import I18nDBworker
from ..controllers.i18n_controller import LocaleController

i18n_cb = CallbackData('i18n', 'type', 'value')

class I18nHandlers(AiogramHandlerPack):
    @staticmethod
    def register(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any]) -> bool:
        dp.register_message_handler(I18nHandlers.cmd_i18n_choose)

        dp.register_callback_query_handler(
            I18nHandlers.query_change_language, i18n_cb.filter(type='lang_choice'))

        return True
    
    @staticmethod
    async def cmd_i18n_choose(message: types.Message, _plugin_name: typing.Any, plugin_config: dict, i18n_controller: LocaleController, _):
        await message.answer(_('Choose your lang'), reply_markup=i18n_controller.get_markup())
    
    @staticmethod
    async def query_change_language(query: types.CallbackQuery, callback_data: dict, plugin_config: typing.Dict, i18n_dbworker: I18nDBworker, i18n_controller: LocaleController):
        await i18n_dbworker.update_user_lang(query.from_user.id, callback_data['value'])
        _ = i18n_controller.get_locale(callback_data['value'])
        await query.message.edit_text(_('Your new language is {}').format(callback_data['value']))
        # NEED TO SEND NEW buttons to user if need
        

