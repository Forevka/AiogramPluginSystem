import json
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.bot import api
from aiogram.utils.payload import generate_payload, prepare_arg, prepare_attachment, prepare_file

import aio_pika
import config
from loguru import logger

def convert_to_dict(key, obj):
    # Populate the dictionary with object meta data
    obj_dict = {
        "attach": key,
        "file_name": obj.file.name
    }

    return obj_dict

class RabbitMQ:
    def __init__(self, routing_key: str, connection_string: str,):
        self.connection_string = connection_string
        self.routing_key = routing_key
        self.connection = None
        self.rmq_channel = None
    
    async def connect(self,):
        self.connection = await aio_pika.connect_robust(self.connection_string)
        self.rmq_channel = await self.connection.channel()
    
    async def message_to_queue(self, method = 'sendMessage', data = None, files = None, **kwargs):
        # Available methods
        # https://github.com/aiogram/aiogram/blob/dev-2.x/aiogram/bot/api.py#L146
        logger.debug(method)
        if files:
            files = [convert_to_dict(key, item) for key, item in files.items()]

        await self.rmq_channel.default_exchange.publish(
                aio_pika.Message(
                    body = json.dumps({
                        'method': method,
                        'data': data,
                        'files': files
                    }).encode('utf-8')
                ),
                routing_key=self.routing_key
            )
        return True