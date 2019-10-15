from .echo_config import config
from aiogram_plugin import WhenToCall
import typing

from aiogram import Dispatcher, types
from loguru import logger

from aiogram_plugin import AiogramPlugin, AiogramHandlerPack


echo_plugin = AiogramPlugin('SimpleEcho', config=config)

def hello_at_start(dp, config: dict):
    logger.info('Hello from simple echo plugin')

class EchoHandlers(AiogramHandlerPack):
    """
        you can simple create you own class
        with your own handlers
    """
    @staticmethod
    def register(dp: Dispatcher, config: typing.Dict[typing.Any, typing.Any]) -> bool:
        dp.register_message_handler(EchoHandlers.echo_message)

        return True
    
    @staticmethod
    async def echo_message(message: types.Message, _plugin_name: typing.Any, plugin_config: dict):
        logger.info(f'Hello from {_plugin_name}')
        logger.info(f'my config is {plugin_config}')
        await message.answer(f'Hello from {_plugin_name} plugin!\nMy config is {plugin_config}')

echo_plugin.plug_handler(EchoHandlers)
echo_plugin.plug_custom_method(hello_at_start, WhenToCall.AT_START)