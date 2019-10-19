
from loguru import logger

from aiogram_plugin import AiogramPlugin
from aiogram_plugin import WhenToCall

from .controllers.db_controller import create_db
from .controllers.i18n_controller import LocaleController
from .handlers.i18n_handlers import I18nHandlers, i18n_cb
from .i18n_config import config
from .middleware.user_locale import GetUserLocale


async def create_i18n_controller(dp, config: dict):
    dp['locale_controller'] = LocaleController(i18n_cb, config)
    dp['i18n_db'] = await create_db(**config['db_i18n_settings'])


i18n_plugin = AiogramPlugin('i18nPlugin', config=config)
i18n_plugin.plug_handler(I18nHandlers)
i18n_plugin.plug_middleware(GetUserLocale)
i18n_plugin.plug_custom_method(create_i18n_controller, WhenToCall.AT_START)
