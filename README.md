# AiogramPluginSystem
[![Updates](https://pyup.io/repos/github/Forevka/AiogramPluginSystem/shield.svg)](https://pyup.io/repos/github/Forevka/AiogramPluginSystem/)
[![Python 3](https://pyup.io/repos/github/Forevka/AiogramPluginSystem/python-3-shield.svg)](https://pyup.io/repos/github/Forevka/AiogramPluginSystem/)



It`s repository with plugin system for Aiogram framework
with this system you can create plugin and attach to him 
all of yours handlers, middlewares, configs and other custom methods

Then simply do 
```
from aiogram_plugin import monkey_patch; monkey_patch(Dispatcher, Handler)
loop.run_until_complete(dp.register_plugin(echo_plugin))
```
and everything setup to dp automatically!

Small example of plugin code:

Importing trivial modules
```
import typing

from aiogram import Dispatcher, types
from loguru import logger
```

importing plugin modules
```
from aiogram_plugin import WhenToCall
from aiogram_plugin import AiogramPlugin, AiogramHandlerPack
```

Some configs
```
from .echo_config import config
```

And at last defining our plugin and describe handlers for this handlerPack
```
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
```

Now you can attach plugin to your dispatcher instance
```
from aiogram_plugin import monkey_patch; monkey_patch(Dispatcher, Handler)
from plugins.simple_echo.simple_echo_plugin import echo_plugin
...
loop.run_until_complete(dp.register_plugin(echo_plugin))
...
```
That`s all!
All code you can find in plugins/echo_plugin directory
